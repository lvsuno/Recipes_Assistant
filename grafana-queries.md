## Queries

### 1. Response Time Panel

This query shows the response time for each conversation within the selected time range:

```sql
SELECT
  timestamp AS time,
  response_time
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
ORDER BY timestamp
```

### 2. Relevance Distribution Panel

This query counts the number of conversations for each relevance category within the selected time range:

```sql
SELECT
  relevance,
  COUNT(*) as count
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
GROUP BY relevance
```

### 3. Model Usage Panel

This query counts the number of times each model was used within the selected time range:

```sql
SELECT
  model_used,
  COUNT(*) as count
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
GROUP BY model_used
```

### 4. Global Token Usage Panel

This query shows the average token usage over time, grouped by Grafana's automatically calculated interval:

```sql
SELECT
  $__timeGroup(timestamp, $__interval) AS time,
  AVG(total_tokens) AS avg_tokens
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
GROUP BY 1
ORDER BY 1
```

### 5. Token Usage per model Panel

This query shows the average token usage per model within the selected time range:

```sql
SELECT
  model_used,
  AVG(total_tokens) AS avg_tokens
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
GROUP BY 1
ORDER BY 1
```

### 6. OpenAI Cost Panel

This query shows the total OpenAI cost over time, grouped  automatically calculated interval:

```sql
SELECT
  $__timeGroup(timestamp, $__interval) AS time,
  SUM(openai_cost) AS total_cost
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
  AND openai_cost > 0
GROUP BY 1
ORDER BY 1
```

### 7. Recent Conversations Panel

This query retrieves the 5 most recent conversations within the selected time range:

```sql
SELECT
  timestamp AS time,
  question,
  answer,
  relevance
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
ORDER BY timestamp DESC
LIMIT 5
```

### 8. Feedback Statistics Panel

This query calculates the total number of positive and negative feedback within the selected time range:

```sql
SELECT
  SUM(CASE WHEN feedback = 0 THEN 1 ELSE 0 END) as Very_BAD,
  SUM(CASE WHEN feedback = 1  THEN 1 ELSE 0 END) as BAD,
  SUM(CASE WHEN feedback = 2 THEN 1 ELSE 0 END) as ACCEPTABLE,
  SUM(CASE WHEN feedback = 3 THEN 1 ELSE 0 END) as GOOD,
  SUM(CASE WHEN feedback = 4 THEN 1 ELSE 0 END) as Excellent
FROM feedbacks
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
```
