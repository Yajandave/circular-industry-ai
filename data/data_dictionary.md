# Data Dictionary

Dataset: `sample_industrial_streams.csv`

This dataset is synthetic and created for portfolio development. It represents industrial material, by-product, waste and resource streams that could appear in a manufacturing or industrial operations environment.

| Field | Type | Description | Example |
|---|---|---|---|
| `stream_id` | text | Unique identifier for each industrial stream. | S001 |
| `stream_name` | text | Name of the material, waste, by-product or resource stream. | Aluminium machining offcuts |
| `material` | text | Broad material or stream category. | metals |
| `source_process` | text | Operational process where the stream is generated. | CNC machining |
| `monthly_quantity_kg` | number | Estimated or measured monthly quantity in kilograms. Energy/resource streams may use 0 when kg is not appropriate yet. | 1850 |
| `current_route` | text | Current management route for the stream. | sold as mixed scrap |
| `disposal_cost_per_month` | number | Current monthly cost in GBP linked to disposal, treatment, handling or contractor route. | 420 |
| `contamination_risk` | low / medium / high / unknown | Initial contamination risk rating for circular use. | low |
| `hazardous_flag` | true / false / unknown | Indicates whether the stream is hazardous or may require specialist compliance review. | false |
| `department` | text | Internal department or function responsible for the stream. | Manufacturing |
| `supplier` | text | Supplier or contractor connected to the stream, where known. | AluForm Metals Ltd |
| `supplier_takeback_available` | yes / no / unknown | Whether a supplier take-back, return loop or reverse logistics route is already known. | unknown |
| `recycled_content_available` | yes / no / unknown | Whether recycled-content alternatives or material recovery options are known to exist. | yes |
| `notes` | text | Contextual notes for future rules, evidence scoring and recommendations. | Clean, segregated aluminium offcuts... |

## Notes for future milestones

The dataset is intentionally designed to support future recommendation logic. For example:

- Hazardous streams should trigger human review.
- Low-contamination, high-volume metal streams may trigger closed-loop recycling review.
- Supplier-linked packaging streams may trigger supplier take-back or returnable packaging review.
- High-volume water or heat streams should not be treated as normal waste mass without additional metering data.
- High-contamination or unknown-composition streams should receive lower confidence scores.
- Streams already under circular routes should be treated as existing good practice rather than inflated as new diversion opportunities.
