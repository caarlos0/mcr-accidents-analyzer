SELECT
  strftime ('%Y', date) AS year,
  SUM(fatal_victims) AS total_fatal_victims,
  count(*) AS total_accidents,
  SUM(
    CASE
      WHEN is_roundabout IS TRUE THEN fatal_victims
      ELSE 0
    END
  ) AS total_roundabout_fatal_victims,
  SUM(
    CASE
      WHEN is_roundabout IS TRUE THEN 1
      ELSE 0
    END
  ) AS total_roundabout_accidents
FROM
  articles
GROUP BY
  strftime ('%Y', date)
ORDER BY
  year
