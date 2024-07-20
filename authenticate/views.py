# Create your views here.
import sys
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from authenticate.models import Palm
from django.http import HttpResponse
import cv2
import fingerprint_enhancer
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib import messages
import os
import numpy as np
import time
import uuid
current_path = os.getcwd()
#sift_matches = os.path.join(current_path, 'result', 'sift_matches.png')


def register(request):
    return render(request, 'register.html')


username = ' '
authenticate = " "
result_dir = None


def saveinfo(request):
    if request.method == 'POST':
        mail = request.POST.get('mail')
        username = request.POST.get('username')
        ph = request.POST.get('ph')
        im = request.FILES.get('im')
        if Palm.objects.filter(email=mail).exists():
            messages.error(request, 'email already exists')
            return redirect('register')
        else:
            if isinstance(im, InMemoryUploadedFile):
                en = Palm(username=username, phnumber=ph, email=mail, picture=im)
                en.save()
                messages.success(request, "Registration successful.")
            else:
                messages.error(request, "Invalid image data provided.")
    return render(request, 'register.html')


def extract_vein_pattern(image):
    gray = image
    noise = cv2.fastNlMeansDenoising(gray)
    noise = cv2.cvtColor(noise, cv2.COLOR_GRAY2BGR)
    print("reduced noise")

    # equalist hist
    kernel = np.ones((7, 7), np.uint8)
    img = cv2.morphologyEx(noise, cv2.MORPH_OPEN, kernel)
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
    img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    print("equalize hist")

    # invert
    inv = cv2.bitwise_not(img_output)
    print("inverted")

    # erode
    gray = cv2.cvtColor(inv, cv2.COLOR_BGR2GRAY)
    erosion = cv2.erode(gray, kernel, iterations=1)
    print("eroded")

    # skel
    img = gray.copy()
    skel = img.copy()
    skel[:, :] = 0
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
    iterations = 0

    while True:
        eroded = cv2.morphologyEx(img, cv2.MORPH_ERODE, kernel)
        temp = cv2.morphologyEx(eroded, cv2.MORPH_DILATE, kernel)
        temp = cv2.subtract(img, temp)
        skel = cv2.bitwise_or(skel, temp)
        img[:, :] = eroded[:, :]
        if cv2.countNonZero(img) == 0:
            break

    print("skel done")
    rt, th = cv2.threshold(skel, 5, 255, cv2.THRESH_BINARY)
    return th


def authenticate(request):
    global result_dir
    if request.method == "POST":
        try:
            # Create the result directory with the unique identifier
            result_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "result")
            os.makedirs(result_dir, exist_ok=True)

            # Read the image from the request
            uploaded_file = request.FILES['im']
            image_path = os.path.join(result_dir, 'palm.png')
            with open(image_path, 'wb') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            print("Image saved successfully as palm.png")

            """sift = cv2.SIFT_create()
            kp1, des1 = sift.detectAndCompute(img1, None)
            kp2, des2 = sift.detectAndCompute(stored_image, None)
            bf = cv2.BFMatcher()
            matches = bf.match(des1, des2)
            matches = sorted(matches, key=lambda x: x.distance)
            result1 = cv2.drawMatches(img1, kp1, stored_image, kp2, matches[:10], None)

            # Save the feature matching result (if needed)
            cv2.imwrite(sift_matches, result1)"""
            # Process the image
            uploaded_file.seek(0)  # Reset file pointer to the beginning
            image_data = uploaded_file.read()
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

            vein_pattern_img = extract_vein_pattern(img)
            vein_pattern_path = os.path.join(result_dir, 'veinpattern.png')
            cv2.imwrite(vein_pattern_path, vein_pattern_img)
            print("Vein pattern saved successfully as veinpattern.png")
            global username
            global authenticate
            username = request.POST.get('username', '')

            try:
                palm_instance = Palm.objects.get(username=username)
                print("Username registered in the DB")
            except Palm.DoesNotExist:
                print("User not registered in the database")
                return redirect('home/')  # Redirect to home if user is not registered

            try:
                print('Analyzing the received palmvein')
                out = fingerprint_enhancer.enhance_Fingerprint(img)  # enhance the palmvein image
                #print('Enhanced vein pattern for received palmvein:', out)
                print('Analyzing the palmvein registered in the DB')
                img2 = cv2.imread('./upload/' + palm_instance.picture.name, 0)  # read input image
                out2 = fingerprint_enhancer.enhance_Fingerprint(img2)  # enhance the palmvein image
                #print('Enhanced vein pattern for registered palmvein:', out2)
                #print('Contents of out:', out)
                #print('Contents of out2:', out2)
                # Comparison
                if isinstance(out, np.ndarray) and isinstance(out2, np.ndarray):
                    result = np.array_equal(out, out2)

                    if result:
                        print("Authenticated!")
                        authenticate = True
                    else:
                        print("Authentication failed!")
                        authenticate = False
                else:
                    print("Authentication failed due to invalid data.")
                    authenticate = False


            except Exception as e:
                print("An error occurred when analyzing the palmvein: ", str(e))

            return redirect('home/')  # Redirect to home regardless of authentication result

        except:
            return redirect('home/')  # Redirect to home if there's an error reading the image

    return render(request, 'authenticate.html')



def home(request):
    global result_dir
    data = {}
    try:
        data['username'] = Palm.objects.filter(username=username).first().username
        data['authenticate'] = authenticate
        uploaded_image = os.path.join("static", "result", "palm.png")# Pass the image path to the template
        extracted_image = os.path.join("static", "result", "veinpattern.png")
        data['uploaded_image'] = uploaded_image
        data['extracted_image'] = extracted_image
        print("Uploaded image path:", uploaded_image)
        print(data)
        return render(request, 'home/index.html', data)
    except:
        data['authenticate'] = False
        return render(request, 'home/index.html', data)










