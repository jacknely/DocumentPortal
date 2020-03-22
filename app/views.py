from flask import Flask, render_template, request, redirect, url_for, flash, Response
from app import app
from settings import S3_BUCKET, S3_KEY, S3_SECRET
import boto3
from .models import PartNumber, BuildPhase, Supplier
from .services import file_type

# initialising aws details from config file
s3 = boto3.client(
    's3',
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET)


@app.route('/')
def index():
    # get all input variables from db
    part_number = PartNumber.query.all()
    build_phase = BuildPhase.query.all()
    supplier = Supplier.query.all()

    return render_template('index.html', part_number=part_number, build_phases=build_phase, suppliers=supplier)


@app.route('/files')
def files():  # TODO add functionality to filter retrieve metadata
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    summaries = my_bucket.objects.all()

    files = []
    for object in summaries:
        bucket = object.bucket_name
        key = object.key
        response = s3.head_object(Bucket=bucket, Key=key)

        file = {'key': key,
                'part_number': response['Metadata']['part_number'],
                'build_phase': response['Metadata']['build_phase'],
                'supplier': response['Metadata']['supplier'],
                'last_modified': object.last_modified,
                }
        files.append(file)

    return render_template('files.html', files=files)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    part_number = request.form['part_number']
    build_phase = request.form['build_phase']
    supplier = request.form['supplier']

    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    my_bucket.Object(file.filename).put(Body=file, Metadata={'part_number': part_number,
                                                             'build_phase': build_phase,
                                                             'supplier': supplier})

    flash('File upload complete')
    return redirect(url_for('files'))


@app.route('/delete', methods=['POST'])
def delete():
    key = request.form['key']

    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    my_bucket.Object(key).delete()

    flash(f'{key} deleted')
    return redirect(url_for('files'))


@app.route('/download', methods=['POST'])
def download():
    key = request.form['key']

    s3_resource = boto3.resource('s3')
    s3_client = boto3.client('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    file_object = my_bucket.Object(key).get()

    return Response(
        file_object['Body'].read(),
        mimetype=file_type(key),
        headers={"Content-Disposition": f"attachment;filename={key}"}
    )