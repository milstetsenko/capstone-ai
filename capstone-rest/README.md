## Usage

This is basic endpoint for serving static images. I am thinking about running the model in real time in the cloud, but there are two problems with this approach:
1. Cost - renting dedicated gpu instance for a year is quite expensive
2. Latency - if I was to run the model, I'd have to make sure that it can serve a lot of conscurrent requests and do it quickly. In order to make it work like that it would require even more money.

Hence I decided to run the model in advance and generate 100,000 images in advance. This way I am just serving static image files which costs us much less yet provides superior user experience.

## Note

If u want to run this locally, you need to populate directory `static/patterns/` with files named with the following convention `pattern_0.png`.
