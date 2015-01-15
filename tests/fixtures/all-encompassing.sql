DO $$
DECLARE the_auth_user_id       uuid;
        the_survey_id          uuid;
        the_from_question_id   uuid;
        the_to_question_id     uuid;
        the_question_choice_id uuid;
BEGIN

INSERT INTO auth_user (email)
VALUES ('test_email')
RETURNING auth_user_id INTO the_auth_user_id;

INSERT INTO survey (title, auth_user_id)
VALUES ('test_title', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 1, 'integer question', 'integer', False, 2),
       (the_survey_id, 5, 'time question', 'time', False, 6),
       (the_survey_id, 6, 'location question', 'location', False, 7),
       (the_survey_id, 7, 'text question', 'text', True, 8),
       (the_survey_id, 9, 'note', 'note', False, -1);

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 2, 'multiple choice question', 'multiple_choice', 
           False, 3)
RETURNING question_id into the_from_question_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 3, 'decimal question', 'decimal', False, 4)
RETURNING question_id into the_to_question_id;

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice 1', 1, the_from_question_id, 'multiple_choice', 2, False,
    the_survey_id)
RETURNING question_choice_id into the_question_choice_id;

INSERT INTO question_branch (question_choice_id, from_question_id,
    from_type_constraint, from_sequence_number, from_allow_multiple,
    from_survey_id, to_question_id, to_type_constraint, to_sequence_number,
    to_allow_multiple, to_survey_id)
VALUES (the_question_choice_id, the_from_question_id, 'multiple_choice', 2,
    False, the_survey_id, the_to_question_id, 'decimal', 3, False,
    the_survey_id);

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 4, 'date question', 'date', False, 5)
RETURNING question_id into the_to_question_id;

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice 2', 2, the_from_question_id, 'multiple_choice', 2, False,
    the_survey_id)
RETURNING question_choice_id into the_question_choice_id;

INSERT INTO question_branch (question_choice_id, from_question_id,
    from_type_constraint, from_sequence_number, from_allow_multiple,
    from_survey_id, to_question_id, to_type_constraint, to_sequence_number,
    to_allow_multiple, to_survey_id)
VALUES (the_question_choice_id, the_from_question_id, 'multiple_choice', 2,
    False, the_survey_id, the_to_question_id, 'date', 4, False,
    the_survey_id);

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, logic, question_to_sequence_number)
VALUES (the_survey_id, 8, 'multiple choice with other question',
           'multiple_choice', False, '{"required": false, "with_other": true}', 9)
RETURNING question_id into the_from_question_id;

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice a', 1, the_from_question_id, 'multiple_choice', 8,
    False, the_survey_id);

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice b', 2, the_from_question_id, 'multiple_choice', 8,
    False, the_survey_id);

INSERT INTO auth_user (email)
VALUES ('a.dahir7@gmail.com')
RETURNING auth_user_id INTO the_auth_user_id;

INSERT INTO survey (title, auth_user_id)
VALUES ('test_title2', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 1, 'another integer question', 'integer', True, 2),
       (the_survey_id, 5, 'another time question', 'time', True, 6),
       (the_survey_id, 6, 'another location question', 'location', True, 7),
       (the_survey_id, 7, 'another text question', 'text', True, 8),
       (the_survey_id, 9, 'another note', 'note', False, -1);

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 2, 'another multiple choice question', 'multiple_choice', 
           False, 3)
RETURNING question_id into the_from_question_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 3, 'another decimal question', 'decimal', True, 4)
RETURNING question_id into the_to_question_id;

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice 1', 1, the_from_question_id, 'multiple_choice', 2, False,
    the_survey_id)
RETURNING question_choice_id into the_question_choice_id;

INSERT INTO question_branch (question_choice_id, from_question_id,
    from_type_constraint, from_sequence_number, from_allow_multiple,
    from_survey_id, to_question_id, to_type_constraint, to_sequence_number,
    to_allow_multiple, to_survey_id)
VALUES (the_question_choice_id, the_from_question_id, 'multiple_choice', 2,
    False, the_survey_id, the_to_question_id, 'decimal', 3, True,
    the_survey_id);

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 4, 'another date question', 'date', True, 5)
RETURNING question_id into the_to_question_id;

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice 2', 2, the_from_question_id, 'multiple_choice', 2, False,
    the_survey_id)
RETURNING question_choice_id into the_question_choice_id;

INSERT INTO question_branch (question_choice_id, from_question_id,
    from_type_constraint, from_sequence_number, from_allow_multiple,
    from_survey_id, to_question_id, to_type_constraint, to_sequence_number,
    to_allow_multiple, to_survey_id)
VALUES (the_question_choice_id, the_from_question_id, 'multiple_choice', 2,
    False, the_survey_id, the_to_question_id, 'date', 4, True,
    the_survey_id);

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, logic, question_to_sequence_number)
VALUES (the_survey_id, 8, 'another multiple choice with other question',
           'multiple_choice', False, '{"required": false, "with_other": true}', 9)
RETURNING question_id into the_from_question_id;

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice a', 1, the_from_question_id, 'multiple_choice', 8,
    False, the_survey_id);

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice b', 2, the_from_question_id, 'multiple_choice', 8,
    False, the_survey_id);

INSERT INTO survey (title, auth_user_id)
VALUES ('what is life', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, logic, question_to_sequence_number)
VALUES (the_survey_id, 1, 'life', 'integer', False, '{"required": true, "with_other": false}', 2),
       (the_survey_id, 2, 'there is none fool', 'note', False, '{"required": false, "with_other": false}', -1);

INSERT INTO survey (title, auth_user_id)
VALUES ('what is death', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, logic, question_to_sequence_number)
VALUES (the_survey_id, 1, 'death', 'integer', False, '{"required": true, "with_other": false}', 2),
       (the_survey_id, 2, 'me', 'note', False, '{"required": false, "with_other": false}', -1);

INSERT INTO survey (title, auth_user_id)
VALUES ('happiness', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, logic, question_to_sequence_number)
VALUES (the_survey_id, 1, 'rate me', 'integer', False, '{"required": true, "with_other": false}', 2),
       (the_survey_id, 3, 'Tell me how you feel', 'text', True, '{"required": true,"with_other": false }', -1),
       (the_survey_id, 2, 'thanks, youre the best', 'note', False, '{"required": false, "with_other": false}', 3);

INSERT INTO survey (title, auth_user_id)
VALUES ('do you like me?', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 1, 'rate me', 'integer', True, 2),
       (the_survey_id, 2, 'will you go out with me?', 'text', True, 3),
       (the_survey_id, 3, 'im gonan ask you out anyway', 'note', False, -1);

INSERT INTO survey (title, auth_user_id)
VALUES ('my favourite number', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 1, 'guess it', 'integer', True, 2),
       (the_survey_id, 2, 'it was 7 btw', 'note', False, 3),
       (the_survey_id, 3, 'also where are you', 'location', False, -1);

INSERT INTO survey (title, auth_user_id)
VALUES ('sadness', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 1, 'rat3e life', 'integer', False, 2),
       (the_survey_id, 3, 'it wasnt', 'note', False, -1),
       (the_survey_id, 2, 'was it really worth it', 'text', True, 3);

INSERT INTO survey (title, auth_user_id)
VALUES ('days of the week', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, logic, question_to_sequence_number)
VALUES (the_survey_id, 1, 'repeat multiple choice with other question',
           'multiple_choice', True, '{"required": false, "with_other": true}', -1)
RETURNING question_id into the_from_question_id;

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice a', 1, the_from_question_id, 'multiple_choice', 1,
    True, the_survey_id),
('choice b', 2, the_from_question_id, 'multiple_choice', 1,
    True, the_survey_id),
('choice c', 3, the_from_question_id, 'multiple_choice', 1,
    True, the_survey_id),
('choice d', 4, the_from_question_id, 'multiple_choice', 1,
    True, the_survey_id);

INSERT INTO survey (title, auth_user_id)
VALUES ('days of the month', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 1, 'guess it', 'integer', False, 2),
       (the_survey_id, 2, 'HA', 'note', False, -1);

INSERT INTO survey (title, auth_user_id)
VALUES ('how many pieces of rope to reach the moon', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 1, 'guess it', 'integer', False, 2),
       (the_survey_id, 2, 'one, if its long enough', 'note', False, -1);
END $$;
