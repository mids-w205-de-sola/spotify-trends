# Project 3: Tracking Spotify Trends

Group members: Jacob Barkow, Stephen Chen, Monali Narayanaswami and Prachi Varma

Our project serves to assemble a pipeline that queries and stores the contents of Spotify's 'Top 50 - Global' playlist, and then analyze those tracks to determine listening trends.

## Business Problem

## File Directory

README.md - You are here

**pipeline**
- docker-compose.yml - The Docker Compose file specifying the images used in the pipeline
- ping_api.py - A Python script that runs a Flask server which queries the Spotify API when pinged and logs the response to Kafka
- extract_playlists.py - A Python script that processes the playlist events in Kafka and stores them in HDFS
- parquet_to_csv.py - A helper Python script which processes the contents of the parquet files and stores them as a CSV
- crontab.txt - The cron commands used to batch automate the process

## Tools Used

- Flask
- Spotify API
- Apache Kafka
- Apache Hadoop
- Apache Spark
- Python

## Data Flow - Setup

The pipeline can be created via the following procedure (note that some directory names may need to be changed depending on your environment):

1. Copy the contents of the pipeline directory onto the server.
2. Use the command `docker compose up -d` to spin up the necessary images. 
3. Create a Kafka topic called 'playlists' via the command `docker-compose exec kafka kafka-topics --create --topic playlists --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181`
4. Launch the Flask server via the command `docker-compose exec mids env FLASK_APP=ping_api.py flask run --host 0.0.0.0`
5. Run the command `crontab -e` to edit the crontab file, add the contents of 'crontab.txt' to it, and save. The currently specified timing is to begin the batch process at 8am PT but can be adjusted accordingly. Adjusting the PATH variable may also be needed depending on your environment.

Once this has been completed, the pipeline will automatically query the Spotify API for the contents of the 'Top 50 - Global' playlist each morning and store the results in HDFS. It will also store the results in a CSV file, which was an intermediary step to help share data across our team. To remove this step, simply take out the final line of the crontab file.

## Data Flow - Explanation

A breakdown of how data flows throughout the system is as follows:

- Once launched, the Flask app on the 'mids' container will listen for requests against http://localhost:5000/. If one is received, it will call the method 'query_playlist', which launches an API GET request for the current contents of the Spotify playlist 'Top 50 - Global'. The result of this request will be a large, deeply-nested JSON, which is then logged to the Kafka topic 'playlists' created previously.
    - We opted to not do additional JSON processing at this stage to preserve the raw data coming from Spotify as best as possible. Extracting the contents of this JSON and then querying the Spotify API for audio features is handled at the very end.
- The Python script 'extract_playlists.py' can be run as a Spark job to process the playlist events queued via the Flask server. When run, this script will take all playlist events in Kafka, munge the timestamp onto each event and then store the results in HDFS. The current implementation overwrites the contents each time it is run.
- The optional Python script 'parquet_to_csv.py' can be run to read the contents of the parquet files created by the Spark job and store them as a CSV. This is not a production-level step and was added to facilitate data sharing across our team and also act as a failsafe in case images went down, as our data is low-fidelity and we have no replication in this system.
    - In a more real-world scenario, we would use Presto to select the value and timestamp fields from the parquet files and convert those into a pandas DataFrame for analysis. The conversion to CSV circumvents this step but would not be appropriate to use in a production setting - it would be best to use something like a dedicated SQL server for permanent storage, rather than CSVs.
- As this data only updates once a day, it was appropriate to run these steps as a batch process. This was accomplished using cron, with the cron commands outlined in the 'crontab.txt' files. The batch timing we used was as follows:
    - 8am PT: ping the Flask server to retrieve that day's Top 50 tracks and log them to Kafka
    - 8:15am PT: run 'extract_playlists' as a Spark job to read the tracks from Kafka and store them in Hadoop
    - 8:30am PT: read the contents of the parquet files and store them as CSVs for internal distribution.