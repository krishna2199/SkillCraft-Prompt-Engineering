Constraint checks for `SCT_PE_1/results`

| Experiment | Constraint | Result | Evidence |
|---|---|---|---|
| 1 original | no unfilled placeholders | FAIL | [Your Email Address], [Your Phone Number], [Your LinkedIn Profile] |
| 1 original | does not claim a resume is attached | FAIL | searched for 'resume attached' |
| 1 improved | 120-160 words | PASS | 146 words |
| 1 improved | has a subject line | FAIL | searched for 'Subject' |
| 1 improved | no unfilled placeholders | PASS | none |
| 1 improved | does not claim a resume is attached | PASS | searched for 'resume attached' |
| 2 improved | prompt's example array is sorted | PASS | [2, 5, 8, 12, 16, 23, 38] |
| 2 improved | worked steps (mid 3 -> 5 -> 4, found at index 4) | PASS | reference run: mids=[3, 5, 4], index=4 |
| 2 improved | 'about 10 comparisons for 1,000 elements' | PASS | floor(log2 1000)+1 = 10 |
| 2 original | printed output (4) matches code | PASS | reference returns 4 |
| 2 original | example target matches code target | FAIL | prose searches 40, code searches 50 |
| 3 original | hashtag count (no limit set) | PASS | 7 hashtags |
| 3 original | no statistics or testimonials | PASS | searched for percentages and quotes |
| 3 improved | 100-140 words | PASS | 125 words excl. hashtags |
| 3 improved | at most 3 hashtags | PASS | 3 hashtags |
| 3 improved | no statistics or testimonials | PASS | searched for percentages and quotes |

12/16 checks passed.
