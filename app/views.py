#imports
from app import app
from flask import request,render_template
import os
from skimage.metrics import structural_similarity
import imutils
import cv2
from PIL import Image

#adding path to config
app.config['INITIAL_FILE_UPLOAD'] = 'app/static/uploads'
app.config['EXISTING_FILE'] = 'app/static/original'
app.config['GENERATED_FILE'] = 'app/static/generated'

#route to home page
@app.route("/",methods = ['GET','POST'])
def index():

    #execute if request is get
    if request.methods == 'GET':
        return render_template("index.html")

    #execute a=if request is POST
    if request.methods =='POST':

        #upload Image
        file_upload = request.files['file_upload']
        filename = file_upload.filename

        #resize and save the uploaded Image
        uploaded_image = Image.open(file_upload).resize((250,160))
        uploaded_image.save(os.path.join(app.config['INITIAL_FILE_UPLOAD'],'image.jpg'))

        #resize and save the original image to ensure both uploaded and original matches in size
        original_image = Image.open(os.path.join(app.cofig['EXISTING_FILE'],'image.jpg'))
        original_image.save(os.path.join(app.config['EXISTING_FILE'],'image.jpg'))

        #read uploaded and original image as array
        original_image = cv2.imread(os.path.join(app.config['EXISTING_FILE'],'image.jpg'))
        uploaded_image = cv2.imread(os.path.join(app.config['INITIAL_FILE_UPLOAD'],'image.jpg'))

        #conver image to grayscale
        original_gray = cv2.cvtColor(original_image,cv2.COLOR_BGR2GRAY)
        uploaded_gray = cv2.cvtColor(uploaded_image,cv2.COLOR_BGR2GRAY)

        #calculate structural_similarity
        (score,diff) = structural_similarity(original_gray,tampered_gray,full = True)
        diff = (diff*255).astype("uint8")

        #calculate threshold and contours
        thresh = cv2.threshold(diff,0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        cnts = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        #draw contours on Image
        for c in cnts:
            (x,y,w,h) = cv2.boundingRect(c)
            cv2.rectangle(original,(x,y),(x+w,y+h),(0,0,255),2)
            cv2.rectangle(tampered,(x,y),(x+w,y+h),(0,0,255),2)

        #save all output images
        cv2.imwrite(os.path.join(app.cofig['GENERATED_FILE'],'image_original.jpg'),original_image)
        cv2.imwrite(os.path.join(app.cofig['GENERATED_FILE'],'image_uploaded.jpg'),uploaded_image)
        cv2.imwrite(os.path.join(app.cofig['GENERATED_FILE'],'image_diff.jpg'),diff)
        cv2.imwrite(os.path.join(app.cofig['GENERATED_FILE'],'image_thresh.jpg'),thresh)
        return render_template('index_html',pred=str(round(score*100,2)) + '%' + 'correct')
#main function
if __main__ == '__main__':
    app.run(debug=True)
