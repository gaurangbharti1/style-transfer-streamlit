import streamlit as st
import requests
import time
import wget

st.title("Neural Style Transfer from Image to Video")
st.markdown('Powered by [Sieve](https://www.sievedata.com)')

# Helper functions

def fetch_video(job_id):
    url = 'https://v1-api.sievedata.com/v1/query/metadata'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': str(st.secrets["SIEVE_API_KEY"])
    }
    data = {
        "job_id": job_id,
        "project_name": "style_transfer_test"
        }
    response = requests.post(url, headers = headers, json=data)
    data = response.json()['data']
    output_video_url = data[0]['output_video']
    output_video = wget.download(output_video_url)
    
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
                    
def get_jobs():
    url = "https://v1-api.sievedata.com/v1/projects/style_transfer_test/jobs"
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
        "project_name": "style_transfer_test",
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
        return (response.json()['job_id'])
    except Exception as e:
        return (f'An error occurred: {e}')
    
#Streamlit App

source_url = st.text_input("Enter source link here") 

image_url = st.text_input("Enter image url here")

style_weight = st.slider("Enter style weight", 0.1, 5.0, 1.0)

content_weight = st.slider("Enter content weight", 0.1, 5.0, 1.0)

if st.button("Send data"):

    st.write("Sending data to sieve...")

    send = send_data(source_url, image_url, style_weight, content_weight)
    with st.spinner('Processing Video'):
        if (check_status('https://v1-api.sievedata.com/v1/projects/style_transfer_test/jobs', 5, str(send))):
            st.video(fetch_video(send))