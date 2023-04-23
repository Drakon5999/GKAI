import './App.css';
import { useState, useEffect } from 'react';
import UploadingForm from './components/UploadingForm';
import JsonViewer from './components/JsonViewer';
import ImageViewer from './components/ImageViewer';
import LoadingSpinner from './components/LoadingSpinner';
import axios from 'axios';
import Box from '@mui/material/Box';


function App() {
  // GKAI is general knowledge artificial intelligence

  // Global state

  // get server and port
  let server = 'localhost:8800'
  const [gkai, setGkai] = useState({});
  const [job, setJob] = useState({});
  const [isLoading, setIsLoading] = useState(false);


  // use interval to check is there job_id in global state
  // if yes, then check status of job
  // if status is done, then get result
  // if result is not null, then show result
  useEffect(
    () => {
      if (job.job_id && job.job_id !== gkai.job_id) {
        setIsLoading(true);
        setGkai({ job_id: job.job_id });
      } else if ((gkai.job_id && gkai.status !== 'DONE' && gkai.status !== 'ERROR')) {
        // check status of job
        axios.get(`http://${server}/job_status?job_id=${gkai.job_id}`)
          .then((response) => {
            if (response.status === 200) {
              setGkai({ ...gkai, status: response.data.status });
            }
          })
          .catch((error) => {
            console.log(error);
          });
      } else if (gkai.job_id && gkai.status === 'DONE' && !gkai.json) {
        // get result of job
        axios.get(`http://${server}/job_result?job_id=${gkai.job_id}`)
          .then((response) => {
            if (response.status === 200) {
              setGkai({ ...gkai, json: response.data });
            }
          })
          .catch((error) => {
            console.log(error);
          });
      } else if (gkai.job_id && gkai.status === 'DONE' && gkai.json && !gkai.image) {
        // get image of job
        axios.get(`http://${server}/job_result_visualisation?job_id=${gkai.job_id}`)
          .then((response) => {
            if (response.status === 200) {
              setGkai({ ...gkai, image: response.data });
              setIsLoading(false);
            }
          })
          .catch((error) => {
            console.log(error);
          });
      }
    }, [gkai, job, server]
  );

  return (
    <div className="App">
      <header className="App-header">
        <h1>
            GKAI Web Application
        </h1>
        <UploadingForm globalState={job} globalStateSetter={setJob} server={server} />
        {isLoading ? <LoadingSpinner /> : <Box />}
        <Box className="App-content" sx={{
            display: 'flex',
            flexDirection: 'row',
            alignContent: 'center',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            width: '100%',
            minWidth: '500px'
        }}>
            <JsonViewer json={gkai.json} key={gkai.json} />
            <ImageViewer image={gkai.image} key={gkai.image} />
        </Box>
      </header>
    </div>
  );
}

export default App;
