from flask_cors import CORS, cross_origin
from flask import Flask, render_template, request, jsonify
import os
import shutil
import time
import requests
from selenium import webdriver

app = Flask(__name__)


@app.route('/',methods= ['GET'])
@cross_origin()

def home():
    return render_template('index.html')
#
# #
@app.route('/imagesp',methods=['GET','POST'])
@cross_origin()
def searchimage():
    if request.method == 'POST':
        sleep_between_interactions = 1
        # target_path = './images'
        # try:    #here we are clearing up pre existing image folder so it doesnt take up much space while deployment.
        #     for a in os.listdir('images'):
        #         shutil.rmtree("./images/"+a)
        # except Exception as e:
        #     print(e)
        # driver_path = './chromedriver'
        # sleep_between_interactions = 0.5
        search_item = request.form.get('content')
        # target_folder = os.path.join(target_path, '_'.join(search_item.lower().split(' ')))
        # if not os.path.exists(target_folder):
        #     os.makedirs(target_folder)
        max_links = 5
        search_item = search_item.split()
        search_item = '+'.join(search_item)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        # driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

        with webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options) as wd:

            url = "https://www.google.co.in/search?q=" + search_item + "&source=lnms&tbm=isch"
            wd.get(url)
            image_urls = set()
            image_count = 0
            results_start = 0
            while image_count < max_links:
                wd.execute_script("window.scrollTo(0, document.body.scrollheight);")
                time.sleep(sleep_between_interactions)
                thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
                number_results = len(thumbnail_results)
                # print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
                # print("FOUND: {} search results . Extracting links from {} till {}".format(number_results, results_start, number_results))

                for img in thumbnail_results[results_start:number_results]:
                    try:
                        img.click()
                        time.sleep(sleep_between_interactions)
                    except Exception:
                        continue
                    actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
                    for actual_image in actual_images:
                        if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                            image_urls.add(actual_image.get_attribute('src'))

                    image_count = len(image_urls)

                    if len(image_urls) >= max_links:
                        # print(f"Found: {len(image_urls)} image links, done!")
                        # print("FOUND: {} image links".format(len(image_urls)))
                        break

                else:
                    # print("Found:", len(image_urls), "image links, looking for more ...")
                    time.sleep(30)
                    return
                    load_more_button = wd.find_element_by_css_selector(".mye4qd")
                    if load_more_button:
                        wd.execute_script("document.querySelector('.mye4qd').click();")
                counter = 0
                # for imgn in image_urls:
                #     #
                #     # try:
                #         # image_content = requests.get(imgn).content
                #
                #     # except Exception as e:
                #     #     print(f"ERROR - Could not download {url} - {e}")
                #
                #     try:
                #         # f = open(os.path.join(target_folder, 'jpg' + "_" + str(counter) + ".jpg"), 'wb')
                #         f = open(os.listdir(target_folder),'wb')
                #         # f.write(image_content)
                #         f.write(imgn)
                #         f.close()
                #         # print(f"SUCCESS - saved {imgn} - as {target_folder}")
                #         counter += 1
                #     except Exception as e:
                #          print(f"ERROR - Could not save {imgn} - {e}")
                # print(image_urls)

        return render_template('showimages.html', user_images=image_urls)
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)


#
