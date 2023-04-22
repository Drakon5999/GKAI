// Ract component form for uploading image file to http://localhost:5000/upload

import React, { Component } from 'react';
import axios from 'axios';

class UploadingForm extends Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedFile: null,
            job_id: null,
            status: null,
            result: null
        }
    }

    // On file select (from the pop up)
    onFileChange = event => {
        // Update the state
        this.setState({ selectedFile: event.target.files[0] });
    };

    // On file upload (click the upload button)
    onFileUpload = () => {
        // Create an object of formData
        const formData = new FormData();

        // Update the formData object
        formData.append(
        "image", // поменяла myFile на image для синхронизации с бэкендом
        this.state.selectedFile,
        this.state.selectedFile.name
        );

        // Details of the uploaded file
        console.log(this.state.selectedFile);

        // Request made to the backend api
        // Send formData object
        axios.post(`http://${this.props.server}/add_job`, formData).then(function (response) {
            this.setState({ job_id: response.data.job_id });
            this.props.globalStateSetter({ job_id: response.data.job_id });
        });

        // save received job_id
    };

    // File content to be displayed after
    // file upload is complete
    fileData = () => {
        if (this.state.selectedFile) {
            return (
                <div>
                <h2>File Details:</h2>
                <p>File Name: {this.state.selectedFile.name}</p>
                <p>File Type: {this.state.selectedFile.type}</p>
                </div>
            );
        }
    };

    render() {
        return (
        <div>
            <h3>
            Upload your image file
            </h3>
            <div>
            <input type="file" onChange={this.onFileChange} />
            <button onClick={this.onFileUpload}>
                Upload!
            </button>
            </div>
            {this.fileData()}
        </div>
        );
    }
}

export default UploadingForm;
