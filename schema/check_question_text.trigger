-- Function: check_question_text_function()

-- DROP FUNCTION check_question_text_function();

CREATE OR REPLACE FUNCTION check_question_text_function()
  RETURNS trigger AS
$BODY$
DECLARE
    the_question_type text;
begin
  SELECT question_type
    into the_question_type
  FROM question
  WHERE question.id = NEW.question_id;
  IF the_question_type != 'text' THEN
    raise exception 'text questions must have answer_text answers';
  end if;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION check_question_text_function()
  OWNER TO postgres;

-- Trigger: check_question_text_trigger on answer_text

-- DROP TRIGGER check_question_text_trigger ON answer_text;

CREATE TRIGGER check_question_text_trigger
  BEFORE INSERT OR UPDATE
  ON answer_text
  FOR EACH ROW
  EXECUTE PROCEDURE check_question_text_function();
