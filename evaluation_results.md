# Evaluation Results — The Unofficial Guide

## Q1: Which apartment complexes near GMU have reported pest problems (cockroaches, mice, or bedbugs)?
- **Expected:** Oakton Park (German cockroaches) and Layton Hall (cockroaches, mice, bedbugs).
- **Retrieved (hybrid, top-5):** Oakton Park, Layton Hall, Apartmentlist Near Gmu, Eaves Fairfax City
- **System answer:** According to the sources, the following apartment complexes near GMU have reported pest problems: 

1. Oakton Park [1] - German cockroaches
2. Layton Hall [2] [5] - cockroaches, mice, and bedbugs
3. Eaves Fairfax City [4] - pest-control concerns (no specific pests mentioned)

## Q2: How much does extra or reserved parking cost at The Point at Fairfax?
- **Expected:** About $100/month for an additional space and $125/month for reserved parking.
- **Retrieved (hybrid, top-5):** The Point At Fairfax, Eaves Fairfax City, Apartmentlist Near Gmu
- **System answer:** According to [1], additional parking spots at The Point At Fairfax cost about $100 per month, and reserved parking costs about $125 per month. This information is also repeated in [2].

## Q3: What is the average rent for an apartment near George Mason University?
- **Expected:** About $2,680 per month.
- **Retrieved (hybrid, top-5):** Commute Neighborhoods Gmu, Apartmentlist Near Gmu, Fairfax Square, Gmu Och Listings
- **System answer:** The average rent for an apartment near George Mason University is about $2,680 per month [1, 2].

## Q4: Which student apartments advertise free CUE bus rides to GMU?
- **Expected:** The Flats on University and The Main on University.
- **Retrieved (hybrid, top-5):** Flats Main On University, Commute Neighborhoods Gmu, Gmu Och Listings
- **System answer:** The Flats on University and The Main on University advertise free CUE bus rides to GMU [1, 2, 5].

## Q5: What do residents say about noise at eaves Fairfax City?
- **Expected:** Neighbors are loud past midnight ('beds shake'); management only enforces quiet hours (10pm-8am).
- **Retrieved (hybrid, top-5):** Eaves Fairfax City
- **System answer:** Residents describe neighbors being loud past midnight, to the point that "beds shake," and say little concrete action is taken [1]. Management can only enforce noise complaints during posted quiet hours (10pm-8am) [2].

## Failure case: Is Oakton Park a good place to live?
- **Expected:** Sources deliberately conflict (high aggregate rating vs. reviews citing roaches, bad parking, and noise) -- expect a one-sided or over-confident answer.
- **Retrieved (hybrid, top-5):** Oakton Park
- **System answer:** I don't have that information in my sources. The sources [1]-[5] provide information on the complaints and praises of residents, but they do not provide an overall assessment of whether Oakton Park is a good place to live. They highlight issues with parking [1, 3], noise [2], and management [5], as well as some positive aspects such as spacious apartments and convenient location [4].

## Hybrid vs. semantic-only retrieval (top-5 source titles)
| Question | Hybrid (semantic + BM25) | Semantic-only |
|---|---|---|
| Q1 | Oakton Park, Layton Hall, Apartmentlist Near Gmu, Eaves Fairfax City | Oakton Park, Layton Hall, Apartmentlist Near Gmu, Commute Neighborhoods Gmu |
| Q2 | The Point At Fairfax, Eaves Fairfax City, Apartmentlist Near Gmu | The Point At Fairfax, Gmu Och Listings, Apartmentlist Near Gmu |
| Q3 | Commute Neighborhoods Gmu, Apartmentlist Near Gmu, Fairfax Square, Gmu Och Listings | Commute Neighborhoods Gmu, Apartmentlist Near Gmu, Gmu Och Listings, Fairfax Square |
| Q4 | Flats Main On University, Commute Neighborhoods Gmu, Gmu Och Listings | Flats Main On University, Commute Neighborhoods Gmu, Gmu Och Listings |
| Q5 | Eaves Fairfax City | Eaves Fairfax City, Fairfax Square |
| Failure case | Oakton Park | Oakton Park |
