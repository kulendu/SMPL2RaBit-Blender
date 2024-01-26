# Running RaBit (locally)


### Vizualising locally
```shell
[1]. git clone https://github.com/kulendu/RaBit
[2]. cd RaBit/
[3]. cd scripts
[4]. sh fetch_assets.sh # downloading all the SMPL pose files 
```

### Installing Polyscope
Follow [this](https://polyscope.run/py/installing/) official tutorial for installing [Polyscope](https://polyscope.run/py/) on Ubuntu.

### Running and visualising 
```shell
python retarget_SMPL_to_RaBit.py vibe_output_2.pkl
```
This will create the renderings by retargeting the motion of SMPL to the RaBit model. The generated assets will be stored in the `assets/` directory.   

![rendering-demo-viz](https://github.com/kulendu/SMPL2RaBit-Blender/blob/main/images/polyscope_vis.png)