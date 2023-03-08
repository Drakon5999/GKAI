// Ract component that beautifully print json in browser
import React from 'react';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import Box from '@mui/material/Box';
import { styled } from '@mui/material/styles';

const MyTypography = styled(Typography)({
    fontFamily: 'monospace',
    whiteSpace: 'pre-wrap',
    wordWrap: 'break-word',
});

const MyPaper = styled(Paper)({
    textAlign: 'left',
    color: (theme) => theme.palette.text.secondary,
});



class JsonViewer extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            json: props.json,
            copied: false,
        };
    }

    render() {
        // do not show component if there is no json
        if (!this.state.json) {
            return null;
        }

        const { copied } = this.state;
        // pretty format json without escaping
        const json = JSON.stringify(JSON.parse(this.state.json), null, 2);
        return (
            <Box sx={{
                flexGrow: 1,
                margin: '50px'
            }}>
                <Grid container spacing={24}>
                    <Grid item xs={12}>
                        <MyPaper>
                            <Box
                                sx={{
                                    border: 1,
                                }}
                            >
                                <MyTypography variant="body1" gutterBottom>
                                    {json}
                                </MyTypography>
                            </Box>
                            <Box
                                sx={{
                                    alignItems: 'center',
                                    bgcolor: 'background.paper',
                                }}
                            >
                                <CopyToClipboard text={json}
                                    onCopy={() => this.setState({ copied: true })}>
                                    <Typography variant="body2" gutterBottom>
                                        {copied ? <span style={{ color: 'red' }}>Copied.</span> : 'Copy to clipboard'}
                                    </Typography>
                                </CopyToClipboard>
                            </Box>
                        </MyPaper>
                    </Grid>
                </Grid>
            </Box>
        );
    }
}

export default JsonViewer;
