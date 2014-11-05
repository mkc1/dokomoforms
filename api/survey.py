"""Functions for interacting with surveys."""
from collections import Iterator
import datetime

from sqlalchemy.engine import RowProxy, Connection

from api import execute_with_exceptions
from db import engine, delete_record, update_record
from db.answer import get_answers_for_question, answer_insert
from db.answer_choice import get_answer_choices_for_choice_id
from db.question import question_insert, get_questions
from db.question_branch import get_branches, question_branch_insert, \
    MultipleBranchError
from db.question_choice import get_choices, question_choice_insert, \
    RepeatedChoiceError, QuestionChoiceDoesNotExistError
from db.submission import get_submissions, submission_insert
from db.survey import survey_insert, survey_select, survey_table, \
    SurveyAlreadyExistsError, get_free_title
from db.type_constraint import TypeConstraintDoesNotExistError


def _create_choices(connection: Connection,
                    values: dict,
                    question_id: str,
                    submission_map: dict) -> Iterator:
    """
    Create the choices of a survey question. If this is an update to an
    existing survey, it will also copy over answers to the questions.

    :param connection: the SQLAlchemy Connection object for the transaction
    :param values: the dictionary of values associated with the question
    :param question_id: the UUID of the question
    :param submission_map: a dictionary mapping old submission_id to new
    :return: an iterable of the resultant choice fields
    """
    old_choices = get_choices(question_id)
    old_choice_dict = {ch.choice: ch.question_choice_id for ch in old_choices}
    new_choices = []
    updates = {}
    for entry in values.get('choices', []):
        try:
            old_choice = entry['old_choice']
            if old_choice not in old_choice_dict:
                raise QuestionChoiceDoesNotExistError(old_choice)
            new_choice = entry['new_choice']
            new_choices.append(new_choice)
            updates[new_choice] = old_choice_dict[old_choice]
        except TypeError:
            new_choices.append(entry)
            if entry in old_choice_dict:
                updates[entry] = old_choice_dict[entry]
    new_choice_set = set(new_choices)
    if len(new_choice_set) != len(new_choices):
        raise RepeatedChoiceError(new_choices)
    for number, choice in enumerate(new_choices):
        choice_dict = {'question_id': question_id,
                       'survey_id': values['survey_id'],
                       'choice': choice,
                       'choice_number': number,
                       'type_constraint_name': values['type_constraint_name'],
                       'question_sequence_number': values['sequence_number'],
                       'allow_multiple': values['allow_multiple']}
        executable = question_choice_insert(**choice_dict)
        exc = [('unique_choice_names', RepeatedChoiceError(choice))]
        result = execute_with_exceptions(connection, executable, exc)
        question_choice_id = result.inserted_primary_key[0]
        yield question_choice_id

        if choice in updates:
            question_fields = {'question_id': question_id,
                               'type_constraint_name': result[1],
                               'sequence_number': result[2],
                               'allow_multiple': result[3],
                               'survey_id': values['survey_id']}
            for answer in get_answer_choices_for_choice_id(updates[choice]):
                answer_values = question_fields.copy()
                new_submission_id = submission_map[answer.submission_id]
                answer_values['question_choice_id'] = question_choice_id
                answer_values['submission_id'] = new_submission_id
                connection.execute(answer_insert(**answer_values))
    #
    # current = get_choices(question_id)
    # existing_choices = {ch.choice: ch.question_choice_id for ch in current}
    # data_choices = values.get('choices', [])
    # # new_choices is a list of the surviving and to-be-created choices
    # new_choices = []
    # # updates is a dictionary for choices which are being renamed
    # updates = {}
    # for entry in data_choices:
    #     try:
    #         old_choice = entry['old_choice']
    #         if old_choice not in existing_choices:
    #             raise QuestionChoiceDoesNotExistError(old_choice)
    #         new_choices.append(old_choice)
    #         updates[entry['old_choice']] = entry['new_choice']
    #     except TypeError:
    #         new_choices.append(entry)
    # new_choice_set = set(new_choices)
    # if len(new_choice_set) != len(new_choices):
    #     raise RepeatedChoiceError(new_choices)
    # for number, choice in enumerate(new_choices):
    #     choice_dict = {'question_id': question_id,
    #                    'survey_id': values['survey_id'],
    #                    'choice': choice,
    #                    'choice_number': number,
    #                    'type_constraint_name': values['type_constraint_name'],
    #                    'question_sequence_number': values['sequence_number'],
    #                    'allow_multiple': values['allow_multiple']}
    #     executable = question_choice_insert(**choice_dict)
    #     exc = [('unique_choice_names', RepeatedChoiceError(choice))]
    #     result = execute_with_exceptions(connection, executable, exc)
    #     yield result.inserted_primary_key[0]


def _create_questions(connection: Connection,
                      questions: list,
                      survey_id: str,
                      submission_map: dict=None) -> Iterator:
    """
    Create the questions of a survey. If this is an update to an existing
    survey, it will also copy over answers to the questions.

    :param connection: the SQLAlchemy Connection object for the transaction
    :param questions: a list of dictionaries, each containing the values
                      associated with a question
    :param survey_id: the UUID of the survey
    :param submission_map: a dictionary mapping old submission_id to new
    :return: an iterable of the resultant question fields
    """
    for number, question in enumerate(questions):
        values = question.copy()
        values['sequence_number'] = number
        values['survey_id'] = survey_id
        if values['allow_multiple'] is None:
            values['allow_multiple'] = False

        existing_question_id = values.pop('question_id', None)

        executable = question_insert(**values)
        tcn = values['type_constraint_name']
        exceptions = [('question_type_constraint_name_fkey',
                       TypeConstraintDoesNotExistError(tcn))]
        result = execute_with_exceptions(connection, executable, exceptions)
        q_id = result.inserted_primary_key[0]

        choices = list(_create_choices(connection, values, q_id,
                                       submission_map=submission_map))

        if existing_question_id is not None:
            question_fields = {'question_id': q_id,
                               'type_constraint_name': result[1],
                               'sequence_number': result[2],
                               'allow_multiple': result[3],
                               'survey_id': survey_id}
            for answer in get_answers_for_question(existing_question_id):
                answer_values = question_fields.copy()
                new_submission_id = submission_map[answer.submission_id]
                answer_values['answer_text'] = answer.answer_text
                answer_values['answer_integer'] = answer.answer_integer
                answer_values['answer_decimal'] = answer.answer_decimal
                answer_values['answer_date'] = answer.answer_date
                answer_values['answer_time'] = answer.answer_time
                answer_values['answer_location'] = answer.answer_location
                answer_values['submission_id'] = new_submission_id
                connection.execute(answer_insert(**answer_values))
                # ans_choices = get_answer_choices_for_question(
                # existing_question_id)
                # for answer_choice in ans_choices:
                # answer_values = question_fields.copy()
                # new_submission_id = submission_map[
                # answer_choice.submission_id]
                # answer_values['question_choice_id'] = None
                # answer_values['submission_id'] = new_submission_id
                # connection.execute(answer_choice_insert(**answer_values))

        yield {'question_id': q_id,
               'type_constraint_name': tcn,
               'sequence_number': values['sequence_number'],
               'allow_multiple': values['allow_multiple'],
               'choice_ids': choices}


def _create_branches(connection: Connection,
                     questions_json: list,
                     question_dicts: list,
                     survey_id: str):
    """
    Create the branches in a survey.

    :param connection: the SQLAlchemy Connection object for the transaction
    :param questions_json: a list of dictionaries coming from the JSON input
    :param question_dicts: a list of dictionaries resulting from inserting
                           the questions
    :param survey_id: the UUID of the survey
    """
    for index, question_dict in enumerate(questions_json):
        from_dict = question_dicts[index]
        from_q_id = from_dict['question_id']
        for branch in question_dict.get('branches', []):
            choice_index = branch['choice_number']
            question_choice_id = from_dict['choice_ids'][choice_index]
            from_tcn = question_dict['type_constraint_name']
            from_mul = from_dict['allow_multiple']
            to_question_index = branch['to_question_number']
            to_question_id = question_dicts[to_question_index]['question_id']
            to_tcn = question_dicts[to_question_index]['type_constraint_name']
            to_seq = question_dicts[to_question_index]['sequence_number']
            to_mul = question_dicts[to_question_index]['allow_multiple']
            branch_dict = {'question_choice_id': question_choice_id,
                           'from_question_id': from_q_id,
                           'from_type_constraint': from_tcn,
                           'from_sequence_number': index,
                           'from_allow_multiple': from_mul,
                           'from_survey_id': survey_id,
                           'to_question_id': to_question_id,
                           'to_type_constraint': to_tcn,
                           'to_sequence_number': to_seq,
                           'to_allow_multiple': to_mul,
                           'to_survey_id': survey_id}
            executable = question_branch_insert(**branch_dict)
            exc = [('question_branch_from_question_id_question_choice_id_key',
                    MultipleBranchError(question_choice_id))]
            execute_with_exceptions(connection, executable, exc)


def _copy_submission_entries(connection: Connection,
                             existing_survey_id: str,
                             new_survey_id: str) -> tuple:
    """
    Copy submissions from an existing survey to its updated copy.

    :param connection: the SQLAlchemy connection used for the transaction
    :param existing_survey_id: the UUID of the existing survey
    :param new_survey_id: the UUID of the survey's updated copy
    :return: a tuple containing the old and new submission IDs
    """
    for submission in get_submissions(existing_survey_id):
        values = {'submitter': submission.submitter,
                  'survey_id': new_survey_id}
        result = connection.execute(submission_insert(**values))
        yield submission.submission_id, result.inserted_primary_key[0]


def _create_survey(connection: Connection, data: dict) -> str:
    """
    Use the given connection to create a survey within a transaction. If
    this is an update to an existing survey, it will also copy over existing
    submissions.

    :param connection: the SQLAlchemy connection used for the transaction
    :param data: a JSON representation of the survey
    :return: the UUID of the survey in the database
    """
    is_update = 'survey_id' in data

    survey_id = None

    # user_id = json_data['auth_user_id']
    title = data['title']
    data_q = data.get('questions', [])

    # First, create an entry in the survey table
    safe_title = get_free_title(title)
    survey_values = {  # 'auth_user_id': user_id,
                       'title': safe_title}
    executable = survey_insert(**survey_values)
    exc = [('survey_title_survey_owner_key',
            SurveyAlreadyExistsError(safe_title))]
    result = execute_with_exceptions(connection, executable, exc)
    survey_id = result.inserted_primary_key[0]

    submission_map = None
    if is_update:
        submission_map = {entry[0]: entry[1] for entry in
                          _copy_submission_entries(connection,
                                                   data['survey_id'],
                                                   survey_id)}

    # Now insert questions.  Inserting branches has to come afterward so
    # that the question_id values actually exist in the tables.
    questions = list(_create_questions(connection, data_q, survey_id,
                                       submission_map=submission_map))
    _create_branches(connection, data_q, questions, survey_id)

    return survey_id


def create(data: dict) -> dict:
    """
    Create a survey with questions.

    :param data: a JSON representation of the survey to be created
    :return: a JSON representation of the created survey
    """

    survey_id = None

    with engine.begin() as connection:
        survey_id = _create_survey(connection, data)

    return get_one(survey_id)


def _get_choice_fields(choice: RowProxy) -> dict:
    """
    Extract the relevant fields from a record in the question_choice table.

    :param choice: A RowProxy for a record in the question_choice table.
    :return: A dictionary of the fields.
    """
    return {'question_choice_id': choice.question_choice_id,
            'choice': choice.choice,
            'choice_number': choice.choice_number}


def _get_branch_fields(branch: RowProxy) -> dict:
    """
    Extract the relevant fields from a record in the question_branch table.

    :param branch: A RowProxy for a record in the question_branch table.
    :return: A dictionary of the fields.
    """
    return {'question_choice_id': branch.question_choice_id,
            'to_question_id': branch.to_question_id}


def _get_fields(question: RowProxy) -> dict:
    """
    Extract the relevant fields from a record in the question table.

    :param question: A RowProxy for a record in the question table.
    :return: A dictionary of the fields.
    """
    result = {'question_id': question.question_id,
              'title': question.title,
              'hint': question.hint,
              'required': question.required,
              'sequence_number': question.sequence_number,
              'allow_multiple': question.allow_multiple,
              'type_constraint_name': question.type_constraint_name,
              'logic': question.logic}
    if question.type_constraint_name.startswith('multiple_choice'):
        choices = get_choices(question.question_id)
        result['choices'] = [_get_choice_fields(choice) for choice in choices]
        branches = get_branches(question.question_id)
        if branches.rowcount > 0:
            result['branches'] = [_get_branch_fields(brn) for brn in branches]
    return result


def _to_json(survey: RowProxy) -> dict:
    """
    Return the JSON representation of the given survey

    :param survey: the survey object
    :return: a JSON dict representation
    """
    questions = get_questions(survey.survey_id)
    question_fields = [_get_fields(question) for question in questions]
    return {'survey_id': survey.survey_id,
            'title': survey.title,
            'questions': question_fields}


def get_one(survey_id: str) -> dict:
    """
    Get a JSON representation of a survey.

    :param data: JSON containing the UUID of the survey
    :return: the JSON representation.
    """
    survey = survey_select(survey_id)
    return _to_json(survey)


# TODO: restrict this by user
# def get_many(data: dict) -> dict:
def get_many() -> dict:
    """
    Return a JSON representation of all the surveys. In the future this will
    be on a per-user basis.

    :return: the JSON string representation
    """
    surveys = survey_table.select().execute()
    return [_to_json(survey) for survey in surveys]


def update(data: dict):
    """
    Update a survey (title, questions). You can also add or modify questions
    here. Note that this creates a new survey (with new submissions, etc),
    copying everything from the old survey. The old survey's title will be
    changed to end with "(new version created on <time>)".

    :param data: JSON containing the UUID of the survey and fields to update.
    """
    survey_id = data['survey_id']
    existing_survey = survey_select(survey_id)
    update_time = datetime.datetime.now()

    new_survey_id = None
    with engine.connect() as connection:
        new_title = '{} (new version created on {})'.format(
            existing_survey.title, update_time.isoformat())
        executable = update_record(survey_table, 'survey_id', survey_id,
                                   title=new_title)
        exc = [('survey_title_survey_owner_key',
                SurveyAlreadyExistsError(new_title))]
        execute_with_exceptions(connection, executable, exc)

        new_survey_id = _create_survey(connection, data)
        # data_q = data.get('questions', [])
        # with engine.connect() as conn:
        # if existing_survey.title != data['title']:
        # safe_title = get_free_title(data['title'])
        # executable = update_record(survey_table,
        # 'survey_id',
        # survey_id,
        # title=safe_title)
        # exc = [('survey_title_survey_owner_key',

    # SurveyAlreadyExistsError(safe_title))]
    # execute_with_exceptions(conn, executable, exc)
    # # The branches need to be deleted first to avoid problems with the
    # # constraint that a branch needs to point forward.
    # _clear_branches(conn, survey_id)
    # questions = list(_create_questions(conn, data_q, survey_id))
    # _create_or_update_branches(conn, data_q, questions, survey_id)

    return get_one(new_survey_id)


def delete(survey_id: str):
    """
    Delete the survey specified by the given survey_id

    :param survey_id: the UUID of the survey
    """
    with engine.connect() as connection:
        connection.execute(delete_record(survey_table, 'survey_id', survey_id))
    return {'message': 'Survey deleted'}
