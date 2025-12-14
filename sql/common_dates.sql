SELECT date
FROM UDate
WHERE uID IN (
    SELECT uID
    FROM Group_members
    WHERE gID = ?
)
GROUP BY date
HAVING COUNT(DISTINCT uID) = (
    SELECT COUNT(*)
    FROM Group_members
    WHERE gID = ?
)
ORDER BY date;
