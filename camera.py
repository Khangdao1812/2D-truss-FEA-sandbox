import pygame as pg #Nếu gọi get event twice là bị bug do event.type.get() consume toàn bộ event queue
import math
class Camera_class() :
    def __init__(self,camx,camy,zoom) : 
        self.camx = camx
        self.camy = camy
        self.zoom = zoom
        self.dragging = False
        self.screen_x = 800
        self.screen_y = 600
        self.scale = 50
        self.zoom_factor = math.sqrt(self.zoom)


    def handle_clicking(self,event) :  #fix để gán biến trực tiếp từ pg trong main
        #print('handling clicking')
        if event.type == pg.MOUSEBUTTONDOWN : 
            if event.button ==1 : 
                self.dragging = True
                self.last_mouse = pg.mouse.get_pos()   
        if event.type == pg.MOUSEBUTTONUP :
            if event.button ==1 : 
                self.dragging = False

    def update_camera(self) :
        if self.dragging :
            self.current_mouse = pg.mouse.get_pos()
            dx = self.current_mouse[0] - self.last_mouse[0]
            dy = self.current_mouse[1] - self.last_mouse[1]
            self.camx -= dx/(self.zoom)
            self.camy -= dy/(self.zoom)
            self.camy = min(3,self.camy)
            self.last_mouse = self.current_mouse

    def update_zoom(self,event,scrx,scry,scale) : 
        if event.type == pg.MOUSEWHEEL: 
            self.current_mouse = pg.mouse.get_pos()
            world_mouse_x = (self.current_mouse[0] + self.camx - scrx//2)/(self.zoom*scale)
            world_mouse_y = (self.current_mouse[1]+self.camy-scry)/(-self.zoom*scale)
            if event.y > 0 and self.zoom < 7.2: 
                self.zoom +=0.1
            if event.y < 0 and self.zoom > 0.4: 
                self.zoom -= 0.1
            self.camx = int(world_mouse_x*scale*self.zoom + scrx//2)-self.current_mouse[0]
            self.camy = min(3,int(scry-world_mouse_y*scale*self.zoom) - self.current_mouse[1])
            self.zoom_factor = math.sqrt(self.zoom)

            #print(self.camx,int(scry-world_mouse_y*scale*self.zoom) - self.current_mouse[1])
#At idle spawning point, px = 300, py = 600
#mouse on screen =(int(x_input*scale*zoom + scrx//2)-camera_object.camx, int(scry-y_input*scale*zoom)-camera_object.camy)

