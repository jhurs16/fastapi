CREATE OR REPLACE VIEW V_MEASURE_TOPICS AS

SELECT
    CASE
        WHEN SUBSTR(ESG.ESG_MEASURE_KEY,1,1) = 'E'
        THEN 'Mögliche Massnahmen im Bereich Umwelt'
        WHEN SUBSTR(ESG.ESG_MEASURE_KEY,1,1) = 'S'
        THEN 'Mögliche Massnahmen im Bereich Gesellschaft'
        WHEN SUBSTR(ESG.ESG_MEASURE_KEY,1,1) = 'G'
        THEN 'Mögliche Massnahmen im Bereich Wirtschaft'
    END AS MEASURE_TOPIC,
    CASE
        WHEN SUBSTR(ESG.ESG_MEASURE_KEY,1,1) = 'E'
        THEN 'Umwelt'
        WHEN SUBSTR(ESG.ESG_MEASURE_KEY,1,1) = 'S'
        THEN 'Gesellschaft'
        WHEN SUBSTR(ESG.ESG_MEASURE_KEY,1,1) = 'G'
        THEN 'Wirtschaft'
    END AS MEASURE_TOPIC_SHORT,
       CASE
        WHEN SUBSTR(ESG.ESG_MEASURE_KEY,1,1) = 'E'
        THEN 1
        WHEN SUBSTR(ESG.ESG_MEASURE_KEY,1,1) = 'S'
        THEN 2
        WHEN SUBSTR(ESG.ESG_MEASURE_KEY,1,1) = 'G'
        THEN 3
    END AS MEASURE_TOPIC_SORT_ORDER 
FROM ESG_MEASURES ESG
WHERE ESG.ESG_MEASURE_KEY!=''
GROUP BY 
    SUBSTR(ESG.ESG_MEASURE_KEY,1,1);