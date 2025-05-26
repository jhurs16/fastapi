DELIMITER $
$

CREATE PROCEDURE DeleteQuestionaire(IN questionaire_id INT UNSIGNED)
BEGIN
    -- Declare an exit handler for SQLEXCEPTION
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        -- Rollback the transaction in case of an error
        ROLLBACK;
    END;

    -- Start a new transaction
    START TRANSACTION;

    -- Delete all answers related to the questionaire
    DELETE FROM ESG_QUESTIONAIRE_ANSWERS WHERE ESG_QUESTIONAIRE_ID = questionaire_id;

    -- Now delete the questionaire itself
    DELETE FROM ESG_QUESTIONAIRES WHERE ESG_QUESTIONAIRE_ID = questionaire_id;

    -- Commit the transaction
    COMMIT;
END
$$

DELIMITER ;

/*

CALL DeleteQuestionaire(1);


*/
