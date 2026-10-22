Constraint checks for `SCT_PE_1/results/rerun_qwen2.5-3b`

| Experiment | Constraint | Result | Evidence |
|---|---|---|---|
| 1 original | no unfilled placeholders | FAIL | [Your Company], [HR Manager's Name], [Your Name], [Your Company], [Your Company], [mention a specific reason, like their products, services, or the company's values that appeal to you], [Your Education Level], [Your University Name], [Your Major/Field of Study], [Your Company], [mention a specific aspect of the company, such as innovation, sustainability, or community involvement], [Your Company], [Your Company], [Your Name], [Your Contact Information], [Your Email Address] |
| 1 original | does not claim a resume is attached | PASS | searched for 'resume attached' |
| 1 improved | 120-160 words | FAIL | 100 words |
| 1 improved | has a subject line | PASS | searched for 'Subject' |
| 1 improved | no unfilled placeholders | FAIL | [Your Name] |
| 1 improved | does not claim a resume is attached | PASS | searched for 'resume attached' |
| 2 improved | prompt's example array is sorted | PASS | [2, 5, 8, 12, 16, 23, 38] |
| 3 original | hashtag count (no limit set) | PASS | 0 hashtags |
| 3 original | no statistics or testimonials | PASS | searched for percentages and quotes |
| 3 improved | 100-140 words | FAIL | 35 words excl. hashtags |
| 3 improved | at most 3 hashtags | PASS | 3 hashtags |
| 3 improved | no statistics or testimonials | PASS | searched for percentages and quotes |
| 1 original | response not truncated | PASS | 349 tokens, done_reason=stop |
| 1 improved | response not truncated | PASS | 117 tokens, done_reason=stop |
| 2 original | response not truncated | FAIL | 2048 tokens, done_reason=length |
| 2 improved | response not truncated | PASS | 1791 tokens, done_reason=stop |
| 3 original | response not truncated | PASS | 86 tokens, done_reason=stop |
| 3 improved | response not truncated | PASS | 52 tokens, done_reason=stop |

13/18 checks passed.
