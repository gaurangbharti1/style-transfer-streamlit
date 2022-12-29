import streamlit as st
import requests
import time
import wget
from PIL import Image

processing = False

st.title("Video Style Transfer")
st.markdown('Built by [Gaurang Bharti](https://twitter.com/gaurang_bharti) using [Sieve](https://www.sievedata.com)')

st.caption("Note: High Resolution Images and Videos will take longer to process!")

# Helper functions

def fetch_video(job_id):
    url = 'https://v1-api.sievedata.com/v1/query/metadata'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': str(st.secrets["SIEVE_API_KEY"])
    }
    data = {
        "job_id": job_id,
        "project_name": "style_transfer_gpu_20fps"
        }
    response = requests.post(url, headers = headers, json=data)
    data = response.json()['data']
    output_video_url = data[0]['output_video']
    output_video = wget.download(output_video_url)
    print(type(output_video))
    return output_video

def check_status(url, interval, job_id):
    finished = False
    headers = {
        'X-API-Key': str(st.secrets["SIEVE_API_KEY"])
        }
    while True:
        response = requests.get(url, headers=headers)
        data = response.json()['data']
        for job in data:
            if job['job_id'] == job_id:
                if job['status'] == 'processing':
                    time.sleep(interval)
                if job['status'] == 'finished':
                    finished = True
                    return finished
                if job['status'] == 'failed':
                    return job['error']
                    
                
def get_jobs():
    url = "https://v1-api.sievedata.com/v1/projects/style_transfer_gpu_20fps/jobs"
    headers = {
        'X-API-Key': str(st.secrets["SIEVE_API_KEY"])
        }
    response = requests.get(url, headers=headers)
    return len(response.json()['data'])+1

def send_data(source_url, image_url, style_weight, content_weight):
    url = "https://v1-api.sievedata.com/v1/push"
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': str(st.secrets["SIEVE_API_KEY"])
    } 
    
    data = {
        "project_name": "style_transfer_gpu_20fps",
        "source_name": str("input" + str(get_jobs())),
        "source_url": str(source_url),
        "user_metadata": {
            "image_url": str(image_url),
            "style_weight": float(style_weight),
            "content_weight": float(content_weight)
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if ('job_id') not in response.json():
            st.error(response.json()['description'])
            return False
        return (response.json()['job_id'])
    except Exception as e:
        return (f'An error occurred: {e}')
    
#Streamlit App

source_url = st.text_input("Enter video url") 

image_url = st.text_input("Enter image url")

style_weight = 0.67

content_weight = 1

if st.checkbox("Advanced settings"):
    style_weight = st.slider("Enter style weight", 0.1, 5.0, 0.67)

    content_weight = st.slider("Enter content weight", 0.1, 5.0, 1.0)

if st.button("Custom Style Transfer"):
    if source_url == '':
        st.error("Please enter a video url")
    if image_url == '':
        st.error("Please enter an image url")
    if image_url != '' and source_url != '':  
        send = send_data(source_url, image_url, style_weight, content_weight)
        if send:
            with st.spinner('Processing Video'):
                status = check_status('https://v1-api.sievedata.com/v1/projects/style_transfer_gpu_20fps/jobs', 5, str(send))
                if (status == True):
                    video = fetch_video(send)
                    st.video(video)
                else:
                    st.error(status)

st.subheader("Examples")
st.write("Enter the source url and click on one of the buttons below to use that image!")
            
col1, col2, col3 = st.columns(3)       
style_1 = "https://github.com/gaurangbharti1/streamlit-example/raw/master/starry_main.jpg"
style_2 = "https://github.com/gaurangbharti1/streamlit-example/raw/master/the_scream_main.jpg"
style_3 = "https://github.com/gaurangbharti1/streamlit-example/raw/master/wave_main.jpg"

if col1.button("Use style 1"):
    image_url = style_1
    if source_url == '':
        st.error("Please enter source url")
    else:
        processing = True
        send = send_data(source_url, image_url, style_weight, content_weight)
        print(send)
        with st.spinner('Processing Video'):
                status = check_status('https://v1-api.sievedata.com/v1/projects/style_transfer_gpu_20fps/jobs', 5, str(send))
                if (status == True):
                    video = fetch_video(send)
                    st.video(video)
                else:
                    st.error(status)
            
if col2.button("Use style 2"):

    image_url = style_2
    if source_url == '':
        st.error("Please enter source url")
    else:
        processing = True
        send = send_data(source_url, image_url, style_weight, content_weight)
        print(send)
        with st.spinner('Processing Video'):
                status = check_status('https://v1-api.sievedata.com/v1/projects/style_transfer_gpu_20fps/jobs', 5, str(send))
                if (status == True):
                    video = fetch_video(send)
                    st.video(video)
                else:
                    st.error(status)
            
if col3.button("Use style 3"):
    image_url = style_3
    if source_url == '':
        st.error("Please enter source url")
    else:
        processing = True
        send = send_data(source_url, image_url, style_weight, content_weight)
        print(send)
        with st.spinner('Processing Video'):
                status = check_status('https://v1-api.sievedata.com/v1/projects/style_transfer_gpu_20fps/jobs', 5, str(send))
                if (status == True):
                    video = fetch_video(send)
                    st.video(video)
                else:
                    st.error(status)
            
if processing == False:

    with col1:
        image = Image.open("Images/starry.jpeg")
        st.image(image, caption="The Starry Night")
    
    with col2:
        image = Image.open("Images/the_scream.jpg")
        st.image(image, caption="The Scream")
    
    with col3:
        image = Image.open("Images/the_great_wave.jpeg")
        st.image(image, caption="The Great Wave")
