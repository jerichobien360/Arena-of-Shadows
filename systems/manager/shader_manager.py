# systems/shader_manager.py
import moderngl
import pygame
import numpy as np
from OpenGL.GL import *

class ShaderManager:
    """Manages OpenGL shaders for the game using ModernGL."""
    
    def __init__(self):
        # Create ModernGL context from pygame's OpenGL context
        self.ctx = moderngl.create_context()
        self.shaders = {}
        self.frame_buffers = {}
        self.textures = {}
        
        # Default quad for full-screen effects
        self.quad_vertices = np.array([
            -1.0, -1.0, 0.0, 0.0,  # Bottom-left
             1.0, -1.0, 1.0, 0.0,  # Bottom-right
            -1.0,  1.0, 0.0, 1.0,  # Top-left
             1.0,  1.0, 1.0, 1.0   # Top-right
        ], dtype=np.float32)
        
        self.setup_default_shaders()
        self.setup_quad()
    
    def setup_quad(self):
        """Setup a quad for full-screen shader effects."""
        self.quad_vbo = self.ctx.buffer(self.quad_vertices.tobytes())
        self.quad_vao = self.ctx.vertex_array(
            self.shaders.get('default'), 
            [(self.quad_vbo, '2f 2f', 'in_position', 'in_texcoord')]
        )
    
    def setup_default_shaders(self):
        """Load essential shaders for the game."""
        
        # Basic vertex shader for 2D
        vertex_shader = '''
        #version 330 core
        in vec2 in_position;
        in vec2 in_texcoord;
        out vec2 uv;
        
        void main() {
            gl_Position = vec4(in_position, 0.0, 1.0);
            uv = in_texcoord;
        }
        '''
        
        # Post-processing fragment shader
        fragment_shader = '''
        #version 330 core
        in vec2 uv;
        out vec4 fragColor;
        uniform sampler2D u_texture;
        uniform float u_time;
        uniform vec2 u_resolution;
        
        void main() {
            vec4 color = texture(u_texture, uv);
            fragColor = color;
        }
        '''
        
        self.load_shader('default', vertex_shader, fragment_shader)
        
        # Shadow/darkness shader for arena atmosphere
        shadow_fragment = '''
        #version 330 core
        in vec2 uv;
        out vec4 fragColor;
        uniform sampler2D u_texture;
        uniform float u_time;
        uniform vec2 u_player_pos;
        uniform float u_light_radius;
        
        void main() {
            vec4 color = texture(u_texture, uv);
            vec2 pixel_pos = uv * vec2(1920, 1080); // Adjust to your resolution
            
            float dist = distance(pixel_pos, u_player_pos);
            float darkness = smoothstep(0.0, u_light_radius, dist);
            
            // Create flickering shadow effect
            float flicker = sin(u_time * 3.0) * 0.1 + 0.9;
            darkness *= flicker;
            
            color.rgb *= (1.0 - darkness * 0.8);
            fragColor = color;
        }
        '''
        
        self.load_shader('shadows', vertex_shader, shadow_fragment)
        
        # Blood/damage effect shader
        blood_fragment = '''
        #version 330 core
        in vec2 uv;
        out vec4 fragColor;
        uniform sampler2D u_texture;
        uniform float u_damage_intensity;
        uniform float u_time;
        
        void main() {
            vec4 color = texture(u_texture, uv);
            
            // Red tint when damaged
            if (u_damage_intensity > 0.0) {
                float pulse = sin(u_time * 10.0) * 0.5 + 0.5;
                color.r += u_damage_intensity * pulse * 0.5;
                color.gb *= (1.0 - u_damage_intensity * 0.3);
            }
            
            fragColor = color;
        }
        '''
        
        self.load_shader('damage', vertex_shader, blood_fragment)
    
    def load_shader(self, name, vertex_source, fragment_source):
        """Load and compile a shader program."""
        try:
            program = self.ctx.program(
                vertex_shader=vertex_source,
                fragment_shader=fragment_source
            )
            self.shaders[name] = program
            print(f"Shader '{name}' loaded successfully")
        except Exception as e:
            print(f"Failed to load shader '{name}': {e}")
    
    def create_framebuffer(self, name, width, height):
        """Create a framebuffer for render-to-texture effects."""
        texture = self.ctx.texture((width, height), 4)  # RGBA
        fbo = self.ctx.framebuffer(color_attachments=[texture])
        
        self.textures[name] = texture
        self.frame_buffers[name] = fbo
        
        return fbo, texture
    
    def pygame_surface_to_texture(self, surface):
        """Convert pygame surface to OpenGL texture."""
        texture_data = pygame.image.tostring(surface, 'RGBA', True)
        texture = self.ctx.texture(surface.get_size(), 4, texture_data)
        return texture
    
    def render_with_shader(self, shader_name, uniforms=None):
        """Render using specified shader with optional uniforms."""
        if shader_name not in self.shaders:
            return
        
        shader = self.shaders[shader_name]
        
        # Set uniforms if provided
        if uniforms:
            for name, value in uniforms.items():
                try:
                    if name in shader:
                        shader[name].value = value
                except:
                    pass  # Uniform doesn't exist or wrong type
        
        # Render the quad
        self.quad_vao.render()
    
    def begin_post_process(self, framebuffer_name):
        """Begin rendering to a framebuffer for post-processing."""
        if framebuffer_name in self.frame_buffers:
            self.frame_buffers[framebuffer_name].use()
    
    def end_post_process(self):
        """End framebuffer rendering and return to default."""
        self.ctx.screen.use()
    
    def cleanup(self):
        """Clean up OpenGL resources."""
        for shader in self.shaders.values():
            shader.release()
        for fbo in self.frame_buffers.values():
            fbo.release()
        for texture in self.textures.values():
            texture.release()
