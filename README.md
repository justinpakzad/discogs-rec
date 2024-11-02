# Discogs Rec
Discogs Rec is a recommender system that utilizes Spotify's [Annoy](https://github.com/spotify/annoy) library. It is trained on data from the Discogs data dumps, as well as additional data such as user wants, haves, and pricing collected via webscraping. At the moment Discogs Rec only supports recommendations for electronic music listed on Discogs. The idea behind the project was to enhance the digging experience by allowing users to input URLs of releases that they were interested in and receive the top N recommendations back, in order to aid in discovering new music that they might not have discovered on their own. This was a personal project I worked on in my spare time, so by no means is it perfect.


## Repository Structure
- `src/`: Contains the source code for the creation of the Recommender System. This includes the preprocessing of the features used to build the model, generating the .ann file, and creating the mappings between release ids and artist/track titles.
- `app/`: Contains the code for deploying and serving the Recommender System as a web application.

## Setup
1. In order to succesfully generate the Annoy Index you will need the actual dataset, which you can download [here](https://drive.google.com/file/d/1fxCiMm5rDNlEl7bxkLJS91ap3vBMLiOQ/view?usp=sharing). Once downloaded, place it in the `src/data` directory. 
 

2. Clone the repository:
```bash
git clone my_repo
```

## Docker Configuration

The `docker-compose.yaml` file configures two main services: `discogs_rec` for pre processing the data, generating the Annoy index, and data mappings.`fast_api` for the API and Streamlit components.

Shared volumes are configured for directories like `app/mappings`, `app/ann_files`, and `src/data`, so that each service has access to necessary files without duplication.

Please note, in order to run the discogs_rec container, you will need at least 8gb of RAM.
### Docker Commands for Building and Running Services Locally

To build and run the `discogs_rec` and `fast_api` services with `docker-compose`, use the following commands:
```bash
docker compose up --build discogs_rec
```
Or to specify a subset of features to be used:
```bash
docker compose run --build discogs_rec python main.py --features avg_rating low median high countries styles
```
Once finished you can then run the fast_api services and get your recommendations using the following:
```bash
docker compose up fast_api --build
```


## Streamlit App Example
![Alt text](images/demo.png)


