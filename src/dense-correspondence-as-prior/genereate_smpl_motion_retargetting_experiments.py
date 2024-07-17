## Code to generate SMPL motion retargetting experiments. 
## Usage: python genereate_smpl_motion_retargetting_experiments.py 

import os
import sys
import argparse
import numpy as np 

# Insert the local directory at the beginning of sys.path
sys.path.insert(0, 'smplx/smplx')

# Now import the package
import smplx
import torch


# Load from modules 
from constants import parser,get_logger
from renderer import Visualizer


class Mesh: 
    def __init__(self,parametric_model,**kwargs):

        self.parametric_model = parametric_model
        for k in kwargs: 
            self.__dict__[k] = kwargs[k]

        if parametric_model == 'SMPL':
            model_path = 'parametric_models/SMPL_NEUTRAL.pkl'
            self.model = smplx.create(model_path, model_type='smpl', gender='neutral', ext='pkl',
                                num_betas=10, num_pca_comps=12, batch_size=self.cmd_args.batch_size, 
                                create_global_orient=True, create_transl=True,                                
                                create_body_pose=True, create_betas=True,

                                create_left_hand_pose=False, create_right_hand_pose=False,
                                create_expression=False, create_jaw_pose=False,
                                create_leye_pose=False, create_reye_pose=False,
                                ).to(self.device)
            
        
        elif parametric_model == 'RABIT': 
            raise NotImplementedError("Write code to extract vertices and faces for RABIT")   
    

        self.initialize_mesh_sequence()

    def initialize_mesh_sequence(self):
        
        if self.parametric_model == 'SMPL':
            with torch.no_grad():
                model_output = self.model(return_verts=True)
                 
                # Dynamic variables
                self.vertices = model_output.vertices.detach().cpu().numpy()
                self.joints = model_output.joints.detach().cpu().numpy()
                self.joints = self.joints[:,:24] # Need only the first for now
 

            # Static variables
            self.faces = self.model.faces.copy()
            self.lbs_weights = self.model.lbs_weights.detach().cpu().numpy()
            self.vertex2joints = self.model.J_regressor.detach().cpu().numpy()
            self.kinematic_tree = self.model.parents.detach().cpu().numpy()
            self.kinematic_tree[0] = 0 # Root node is parent to itself

        else: 
            raise NotImplementedError("Only works for SMPL. Not for parametric model:{self.parametric_model}")  

        # Auxillary variables
        self.nT, self.nV, self.D = self.vertices.shape        
        assert self.D == 3, 'Only 3D vertices are supported got: {}'.format(self.D)

        # Initial 1-1 mapping between SMPL and vertices
        self.mapping = np.arange(self.nV) 

        return self.get_mesh_sequence()

    def get_mesh_sequence(self):

        return {'vertices': self.vertices, 'faces': self.faces,
                'mapping': self.mapping,
                'lbs_weights': self.lbs_weights,
                'joints': self.joints,
                'kinematic_tree' : self.kinematic_tree,
                'vertex2joints': self.vertex2joints
                }



    def distorte(self,method):
        if method == 'remesh':
            new_indices = np.random.permutation(self.model.v_template.shape[0])
            self.mappping = self.update_mapping(new_indices)


        elif method == 'decimate':
            simplified_mesh = mesh.simplify_quadratic_decimation(target_faces=desired_number_of_faces)

        elif method == 'subdivide': 
            # Subdivide the mesh to increase the number of faces
            subdivided_mesh = mesh.subdivide()

        elif method == 'gaussian noise':
            args.gaussian_noise_std = 0.01 * self.get_bounding_box() # Distrort vertices by 1% of the bounding box. 
            noise = np.random.normal(0, args.gaussian_noise_std, self.nV)

    def update_mapping(self,target):
        # assert source.model == 'SMPL' and source.distortion == '', f"Current experiments assume the source to be the  SMPL model in T-pose and no distorion"

        # Hash join: https://www.geeksforgeeks.org/difference-between-hash-join-and-sort-merge-join/
        # Build 

        # Probe
        # Step 1: Initialize
        # source_mapping = {smpl_index: source_index for smpl_index, source_index in smpl_to_source.T}
        
        # # Step 3: Create the final mapping
        # final_pairs = []
        # for smpl_index, target_index in smpl_to_target.T:
        #     if smpl_index in source_mapping:
        #         # This SMPL index has a corresponding Source index
        #         source_index = source_mapping[smpl_index]
        #         final_pairs.append([source_index, target_index])
        
        # # Step 4: Convert to numpy.ndarray
        # final_mapping = np.array(final_pairs).T  # Transpose to get 2xM shape
    
        # return final_mapping

        # Example usage
        # smpl_to_source = np.array([[SMPL indices], [Source indices]])
        # smpl_to_target = np.array([[SMPL indices], [Target indices]])
        # final_mapping = inner_join_mappings(smpl_to_source, smpl_to_target)
        raise NotImplementedError("Write code to update the mapping. Using hash join")

def save_experiments(args,source,target):
    raise NotImplementedError("Write code to save the experiments")

def render(args,source,target):
    raise NotImplementedError("Write code to render the experiments")


def main(args):

    # Create experiement directory 
    args.out_dir  = os.path.join(args.out_dir,args.exp_name)
    os.makedirs(args.out_dir,exist_ok=True)

    # Create a logger to print and log resutlts
    logger = get_logger(out_dir=args.out_dir,debug=args.debug)
    logger.info("Creating Experiment with arguements: {}".format(args))

    if os.path.exists(os.path.join(args.out_dir,f'{args.exp_name}.pkl')) and not args.force: # If data already exists and we are not forcing to overwriting
        logger.info(f"Setup already exists at:{os.path.join(args.out_dir,f'{args.exp_name}.pkl')}. Skipping")    
        return 


    visualizer = Visualizer() if args.render else None #Create a polyscope visualizer if we are rendering

    device = torch.device('cuda' if torch.cuda.is_available() and args.gpu else 'cpu')

    # Create source mesh
    # Create arguments for source mesh 

    source = Mesh(args.source,visualizer=visualizer,logger=logger,cmd_args=args,device=device)

    # Create target mesh
    target = Mesh(args.target,visualizer=visualizer,logger=logger,cmd_args=args,device=device)
    target.distorte('remesh')
    target.distorte(args.distorion)
    

    # Retarget Everything
    if args.out.dir != '':
        save_experiments(args,source,target)
    
    if args.render:
        render_experiments(args,source,target)    

if __name__ == '__main__':

    cmd_line_args = parser.parse_args()
    print("Arguments:",cmd_line_args)
    main(cmd_line_args)    
    