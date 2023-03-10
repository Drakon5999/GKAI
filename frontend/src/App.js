import './App.css';
import { useState } from 'react';
import UploadingForm from './components/UploadingForm';
import JsonViewer from './components/JsonViewer';
import ImageViewer from './components/ImageViewer';
import axios from 'axios';


function App() {
  // GKAI is general knowledge artificial intelligence

  // Global state
  let server = 'http://localhost:5000';
  const [gkai, setGkai] = useState({});
  const [job, setJob] = useState({});

  // use interval to check is there job_id in global state
  // if yes, then check status of job
  // if status is done, then get result
  // if result is not null, then show result
  const checkJobStatus = () => {
    if (gkai.checkJobStatus) {
      return;
    }

    setGkai({ ...gkai, checkJobStatus: true });
    if (gkai.job_id && gkai.status !== 'DONE' && gkai.status != 'ERROR' || job.job_id && job.job_id != gkai.job_id) {
      // check status of job
      setGkai({ ...gkai, job_id: job.job_id });
      axios.get(`http://${server}/job_status?job_id=${gkai.job_id}`)
        .then((response) => {
          console.log(response);
          if (response.status === 200) {
            setGkai({ ...gkai, status: response.data.status });
          }
        })
        .catch((error) => {
          console.log(error);
        });
    }

    if (gkai.job_id && gkai.status === 'DONE' && !gkai.json) {
      // get result of job
      axios.get(`http://${server}/job_result?job_id=${gkai.job_id}`)
        .then((response) => {
          console.log(response);
          if (response.status === 200) {
            setGkai({ ...gkai, json: response.data });
          }
        })
        .catch((error) => {
          console.log(error);
        });
    }

    if (gkai.job_id && gkai.status === 'DONE' && gkai.json && !gkai.image) {
      // get image of job
      axios.get(`http://${server}/job_result_visualisation?job_id=${gkai.job_id}`)
        .then((response) => {
          console.log(response);
          if (response.status === 200) {
            setGkai({ ...gkai, image: response.data });
          }
        })
        .catch((error) => {
          console.log(error);
        });
    }

    setGkai({ ...gkai, checkJobStatus: false });
  }

  setInterval(checkJobStatus, 200);

  return (
    <div className="App">
      <header className="App-header">
        <UploadingForm globalState={job} globalStateSetter={setJob} server={server} />
        <JsonViewer json={gkai.json} />
        <ImageViewer image={gkai.image} />
      </header>
    </div>
  );
}

export default App;
