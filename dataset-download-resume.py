import os
import csv
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError

# Create the top-level directory
if not os.path.exists("spy_dataset"):
    os.makedirs("spy_dataset")

last_downloaded_user = None
last_downloaded_image = None

# Check if the file exists that stores the last downloaded image
if os.path.exists("last_downloaded.txt"):
    with open("last_downloaded.txt", "r") as f:
        lines = f.readlines()
        if lines:
            last_downloaded_user, last_downloaded_image = lines[0].strip().split(",")

try:
    with open("proctoring_logs_all.csv", "r") as file:
        reader = csv.DictReader(file, delimiter=",")
        for row in reader:
            user_id = row["userid"]
            image_url = row.get("webcampicture")
            if not image_url:
                print(f"Missing webcampicture column for user {user_id}")
                continue

            if last_downloaded_user is not None and user_id != last_downloaded_user:
                continue

            # Create a subdirectory for each person
            person_dir = os.path.join("spy_dataset", user_id)
            if not os.path.exists(person_dir):
                os.makedirs(person_dir)

            image_counter = len(
                [name for name in os.listdir(person_dir) if os.path.isfile(os.path.join(person_dir, name))])

            # If the last downloaded image is defined, and the current counter is less than or equal to it, continue
            if last_downloaded_image is not None and image_counter <= int(last_downloaded_image):
                continue

            session = requests.Session()
            session.mount("http://", HTTPAdapter(max_retries=3))
            session.mount("https://", HTTPAdapter(max_retries=3))

            try:
                print(f"Downloading image for user {user_id} from url {image_url}")
                response = session.get(image_url)
                if response.status_code != 404:
                    response.raise_for_status()
                    filename = os.path.join(person_dir, f"{user_id}_{image_counter}.png")
                    open(filename, "wb").write(response.content)
                    print(f"Successfully downloaded image for user {user_id}")
                    # write the user_id and image_counter to the file
                    with open("last_downloaded.txt", "w") as f:
                        f.write(f"{user_id},{image_counter}")
                else:
                    print(f"404 error for user {user_id} and url {image_url}")
            except requests.exceptions.HTTPError as errh:
                print(f"HTTP Error: {errh} for user {user_id} and url {image_url}")
            except ConnectionError as errc:
                print(f"Error Connecting: {errc} for user {user_id} and url {image_url}")
            except requests.exceptions.Timeout as errt:
                print(f"Timeout Error: {errt} for user {user_id} and url {image_url}")
            except requests.exceptions.RequestException as err:
                print(f"Something went wrong: {err} for user {user_id} and url {image_url}")

except FileNotFoundError:
    print(f"proctoring_logs_all.csv not found in the current directory")
except csv.Error as e:
    sys.exit(f'file {filename}, line {reader.line_num}: {e}')
