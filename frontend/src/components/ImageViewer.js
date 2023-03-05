// Ract component that print image in browser with zoom in and zoom out functionality

import React from 'react';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import Box from '@mui/material/Box';
import { styled } from '@mui/material/styles';

const MyPaper = styled(Paper)({
    padding: (theme) => theme.spacing.unit * 2,
    textAlign: 'center',
    color: (theme) => theme.palette.text.secondary,
});



class ImageViewer extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            image: props.image,
            scale: 1,
        };
    }

    zoomIn = () => {
        this.setState({ scale: this.state.scale + 0.1 });
    }

    zoomOut = () => {
        this.setState({ scale: this.state.scale - 0.1 });
    }

    render() {
        // do not show component if there is no image
        if (!this.state.image) {
            return null;
        }

        const { scale } = this.state;
        return (
            <Box sx={{
                flexGrow: 1,
            }}>
                <Grid container spacing={24}>
                    <Grid item xs={12}>
                        <MyPaper>
                            <img src={this.state.image} alt="image" style={{ transform: `scale(${scale})` }} />
                            <Tooltip title="Zoom In">
                                <IconButton aria-label="Zoom In" onClick={this.zoomIn}>
                                    <ZoomInIcon />
                                </IconButton>
                            </Tooltip>
                            <Tooltip title="Zoom Out">
                                <IconButton aria-label="Zoom Out" onClick={this.zoomOut}>
                                    <ZoomOutIcon />
                                </IconButton>
                            </Tooltip>
                        </MyPaper>
                    </Grid>
                </Grid>
            </Box>
        );
    }
}

export default ImageViewer;
