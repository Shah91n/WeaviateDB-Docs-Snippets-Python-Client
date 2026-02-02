# 🤖 Query Agent: Optimization Guide

Essential best practices for maximizing the performance of Weaviate Query Agent. By refining schema and property scope, you can significantly improve search accuracy and ensure low-latency responses.

## 1. Foundation: Schema Design

A well-defined schema is the key point for the Query Agent. If the schema is vague, the agent will struggle with the data.

### Data Type Precision

The Agent relies on data types to construct queries. Using the wrong type leads to poor performance and bad results.

- **Numeric:** Use `int` or `number` (never `text` for numbers).
- **Booleans:** Use `boolean` for true/false flags.
- **Text:** exclusively for actual strings.

### Critical to keep in mind:

- **Disable Auto-Schema:** Set `AUTOSCHEMA_ENABLED: false`. This prevents auto-generated types which can be incorrect. It allows you to define everything as you see fit for your data.
- **Add Property Descriptions:** This is the most underrated optimization. Descriptions influence which filters to apply to which properties. Descriptions can be updated easily.
    - *Bad:* `property: "temp"`
    - *Good:* `description: "The maximum operating temperature of the oven in Celsius"`

## 2. Efficiency: Property Management

For collections with many properties (100+), the search space becomes too large for the Agent to process efficiently.

### Using `view_properties`

The most effective way to optimize is to define a **view window**. This limits the properties the Agent sees and considers during a query. Example:

```python
qa = QueryAgent(
    client=client,
    collections=[
        QueryAgentCollectionConfig(
            name="YourCollection",
            # Include only essential properties to boost speed and accuracy
            view_properties=[
                "name",
                "category",
                "price",
                "brand",
                "specifications"
            ],
        ),
    ],
)
```

> **Note:** The `view_properties` configuration must be set via the Python/TypeScript SDK; it cannot currently be configured through the Console UI.

## 3. DOs and DON'Ts

| **Action** | **✅ DO** | **❌ DON'T** |
| --- | --- | --- |
| **Data Types** | Use `int`/`number` for math operations. | Store price or weight as `text`. |
| **Descriptions** | Add detailed descriptions for every field. | Leave descriptions blank or unrelated values. |
| **Scaling** | Use `view_properties` for 100+ fields. | Let the Agent scan 1000+ fields. |

## 4. Performance Matrix

| **Property Count** | **No Optimization** | **With view_properties** | **With Proper Schema** |
| --- | --- | --- | --- |
| **< 100** | ✅ Good | ✅ Excellent | ✅ Excellent |
| **100 - 500** | ⚠️ Degraded | ✅ Excellent | ✅ Excellent |
| **500 - 1000** | ❌ Poor performance | ✅ Excellent | ✅ Excellent |
