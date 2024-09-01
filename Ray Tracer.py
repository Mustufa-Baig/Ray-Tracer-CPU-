import pygame ,math , random, time, Collision
import numpy as np
from PIL import Image
pygame.init()


#-----------------------------------------
with open('config.txt','r') as config:
    l=list(filter(None,config.read().replace("\n",'=').split("=")))
    print('\n',l,'\n')

    'Window settings'
    Size=int(l[1])
    Resolution=int(l[3])


    'Resolution settings'
    Desired_FPS=int(l[5])
    Dynamic_Resolution = True if l[7] == 'True' else False

    Performance_Display=True if l[9] == 'True' else False
    Progressive_Resolustion=True if l[11] == 'True' else False


    'Motion settings'
    Motion=True if l[13] == 'True' else False
    Motion_Scale=int(l[15])


    'Pixel quality and effects'
    Bounces=int(l[17])
    Samples=int(l[19])
    Scanline=True if l[21] == 'True' else False


    'Render settings'
    Save=True if l[23] == 'True' else False
    Save_Format=str(l[25])

    'HDRI'
    hdri_img=str(l[27])


#-----------------------------------------


win=pygame.display.set_mode((int(Size*1.7777),Size))
run =True


def rotx(pos,rot):
    x,y,z=pos

    x_=x
    y_=(y*math.cos(rot))-(z*math.sin(rot))
    z_=(y*math.sin(rot))+(z*math.cos(rot))

    return x_,y_,z_

def roty(pos,rot):
    x,y,z=pos

    x_=(x*math.cos(rot))+(z*math.sin(rot))
    y_=y
    z_=(z*math.cos(rot))-(x*math.sin(rot))

    return x_,y_,z_




def random_vector(normal):
    vector=normalize((random.randint(-360,360),random.randint(-360,360),random.randint(-360,360)))
    dod=np.dot(vector,normal)
    
    if dod>0:
        vector=-vector[0],-vector[1],-vector[2]

    return vector


def normalize(vector):
    x,y,z=vector
    length=(x**2 + y**2 + z**2)**(1/2)
    x/=length
    y/=length
    z/=length
    return x,y,z


def reflect(ray,normal):
    ray=normalize(ray)
    normal=normalize(normal)

    
    dod=np.dot(ray,normal)
    x=ray[0]-2*dod*normal[0]
    y=ray[1]-2*dod*normal[1]
    z=ray[2]-2*dod*normal[2]
    
    return normalize((x,y,z))


def sphere_normal(center,hit_pos):
    x,y,z=center
    a,b,c=hit_pos

    x,y,z=(x-a),(y-b),(z-c)
    
    return normalize((x,y,z))



def reflecc(ball,ray,normal):
    if ball.glossy==1:
        ray=reflect(ray,normal)
        
    elif ball.glossy==0:
        ray=random_vector(normal)
        
    else:
        chance=random.random()
        
        if chance<=ball.glossy:
            ray=reflect(ray,normal)
        else:
            ray=random_vector(normal)
           
    return ray


def bounce_light(Origin,Ray,balls,sky_color,sky_emm,bounces,Samples,pix,size):
    color=sky_color
    intersected=True
    ignore_index=-1

    even_collides=True
    #ray color
    r,g,b=1,1,1
    lum=0

    sr,sg,sb=0,0,0
    sn=0
    
    mag=0
    b_n=0

    for i in range(Samples):
        if even_collides:
            even_collides=False
            intersected=True

            b_n=0
            
            r,g,b=1,1,1
            
            ignore_index=-1
            origin=Origin
            ray=Ray
            
            for bounce in range(bounces):
                if intersected:                    
                    intersection_buffer=-1,0,(0,0,0)
                    index=0
                    intersected=False
                    ignore=False
                    for ball in balls:
                        if(index==ignore_index):
                            ignore=True        
                        else:
                            ignore=False
                            
                        if not(ignore):
                            intersect=Collision.intersect_ray_sphere(origin,ray,ball.pos,ball.radius)
                            if not(intersect==None):
                                dist=(intersect[0]**2+intersect[1]**2+intersect[2]**2)**(1/2)
                                
                                if intersection_buffer[0]==-1:
                                    intersection_buffer=dist,index,intersect
                                else:
                                    if dist<intersection_buffer[0]:
                                        intersection_buffer=dist,index,intersect
                                intersected=True
                                even_collides=True
                        index+=1
                        
                    if intersected:
                        ball=balls[intersection_buffer[1]]
                        if not(ball.emmision and b_n==0):
                            normal=sphere_normal(ball.pos,intersection_buffer[2])
                            
                            #absorbing color into light
                            r*=ball.color[0]/255
                            g*=ball.color[1]/255
                            b*=ball.color[2]/255
                            mag+=1

                            if ball.emmision:
                                intersected=False
                            else:
                                #reflect the ray

                                ray=reflecc(ball,ray,normal)
                                
                                origin=intersection_buffer[2]
                                ignore_index=intersection_buffer[1]


                            
                            
                        else:
                            r*=ball.color[0]/255
                            g*=ball.color[1]/255
                            b*=ball.color[2]/255
                            mag+=1
                            
                            intersected=False
                            lit=True
                            
                    else:
                        intersected=False
                        lit=True

                        if mag>0:
                            normal=sphere_normal(ball.pos,intersection_buffer[2])
                            ray=reflecc(ball,ray,normal)
                            sky_color=sky_col_uv(ray,pix,size)
                        
                        r*=sky_color[0]/255
                        g*=sky_color[1]/255
                        b*=sky_color[2]/255
                        lum=1
                        mag+=1

                    
                
                b_n+=1

                
            sr+=r*lum
            sg+=g*lum
            sb+=b*lum
            
            sn+=1
    
    color = sr/sn, sg/sn, sb/sn
    return color


FME=0.42

def sky_col_uv(vector,hdri,size):
    x,y,z=normalize(vector)
    u=FME+(math.atan2(z,x)/(2*math.pi))
    v=0.5+(math.asin(-y)/math.pi)
    
    u*=size[0]
    v*=size[1]

    u=int(u)
    v=int(v)

    if u>=size[0]:
        u-=size[0]
    if u<0:
        u+=size[0]
    
    if v>=size[1]:
        v-=size[1]
    if v<0:
        v+=size[1]
        
    try:
        r,g,b=hdri[u,v]
    except:
        r,g,b,a=hdri[u,v]
    
    return r,g,b

def pixel_by_pixel(Res,Size,origin,balls,win,scan,bounces,first_frame,prs,times,pix,size):
    w,h=Size
    w/=Res
    h/=Res

    sky_color=135,206,250
    #sky_color=0,0,0
    sky_emm=1
    
    for y in range(int(h)):
        rv=0.5-(y/h)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                return False
            
        for x in range(int(w)):
            ray_vector=((0.5-(x/w))*1.7777,rv,1)

                
            sky_color=sky_col_uv(ray_vector,pix,size)

            #print(x,y)
            last_color=win.get_at((x*Res,y*Res))
            
            color=bounce_light(origin,normalize((ray_vector)),balls,sky_color,sky_emm,bounces,Samples,pix,size)

            times=1
            
            if times==1:
                r,g,b=color
            else:
                r,g,b=(color[0]+last_color[0]/255)/2,(color[1]+last_color[1]/255)/2,(color[2]+last_color[2]/255)/2

            if first_frame or prs:
                #r,g,b=color
                pass

            r*=255
            g*=255
            b*=255
            
            if r>255:
                r=255
            if g>255:
                g=255
            if b>255:
                b=255
            

            pygame.draw.rect(win,(r,g,b),(x*Res,y*Res,Res,Res))
            
        if scan:
            pygame.display.update()

    return True


      
clock=pygame.time.Clock()


if Progressive_Resolustion and not(Dynamic_Resolution):
    Resolution=50
    Samples=1

y_pos=0
x_pos=1
y_angle=92
speed=0.5

fps=0
avg=0,0
live_adjust=Dynamic_Resolution
PR_stable=not(Progressive_Resolustion)

down=False
lowest=(1000,1000)
lag_count=0
t=time.time()
getTicksLastFrame=0

FF=True

def cal_eta(current_frame,render_time):
    return (360-current_frame)*render_time


class ball():
    def __init__(self,pos,radius,color,emm=False,glossy=1):
        self.pos=pos
        self.radius=radius
        self.color=color
        self.emmision=emm
            
        self.glossy=glossy




def tuplize(s):
    return tuple(map(float,s.replace('(','').replace(')','').split(',')))

win.fill((0,0,0))

times=0
prev_sample=Samples
    
Balls=[]

with open("objects.txt",'r') as balls:
    ob=list(filter(None,balls.read().split("\n")))
    for b in ob:
        b=b.split('=')
        if len(b)==5:
            Balls.append(ball(tuplize(b[0]),float(b[1]),tuplize(b[2]),glossy=float(b[4])))
        else:
            Balls.append(ball(tuplize(b[0]),float(b[1]),tuplize(b[2])))

with Image.open(hdri_img) as im:
    pix=im.load()
    size=im.size
               
while run:
    if not(Scanline):
        win.fill((0,0,0))
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
    
    t2=time.time()
    ms = int((t2-t) * 1000)
    t=t2
    try:
        fps=int(1000/ms)
    except:
        pass

    
    t3 = pygame.time.get_ticks()
    dt = (t - getTicksLastFrame) / 1000000000
    getTicksLastFrame = t3

    if Motion:
        y_pos=math.sin(math.radians(y_angle))
        x_pos=math.cos(math.radians(y_angle))
        try:
            #print(ms/10)
            if not(Dynamic_Resolution):
                y_angle+=1
            else:
                y_angle+=Motion_Scale*speed*ms/10
                
        except:
            pass
    
    
    
    
    if Progressive_Resolustion and not(Dynamic_Resolution):
        Resolution-=1
        if Resolution<=4:
            if Resolution<=1:
                Resolution=1
                PR_stable=True
                
            if Samples<1000:
                Samples*=2
        
        print("Resolution: "+str(int(Resolution))+", Samples: "+str(int(Samples))+", Next Frame ETA: "+str(2*(ms/1000))+" Seconds")


    if not(Dynamic_Resolution) and Performance_Display and not(Progressive_Resolustion):
        try:
            print(str(ms/1000)+' seconds')
        except:
            pass
        
    if Dynamic_Resolution and live_adjust:
        if fps>(Desired_FPS*1.75):
            Resolution-=1
            down=True
        else:
            if (fps<Desired_FPS*1.25):
                Resolution+=1
            else:
                if down:
                    live_adjust=False
                    print('Stable !!!')
    
        if Resolution<1:
            Resolution=1

        if down:
            if fps<lowest[0]:
                lowest=fps,Resolution
            if fps<(Desired_FPS*0.75):
                lag_count+=1
                Resolution+=2
                #print("Lag !!")
                
            avg=((avg[0]+fps)/2),((avg[1]+Resolution)/2)


    times+=1
    if not(prev_sample==Samples):
        FF=False

    FME+=0.01
    if FME>=1:
        FME=0
        
    run=pixel_by_pixel(int(Resolution),(Size*1.7777,Size),(0,0,0),Balls,win,Scanline,Bounces,FF,PR_stable,times,pix,size)
    
    prev_sample=Samples
    
    if not(Scanline):
        pygame.display.update()
    
    if y_angle<360 and not(Dynamic_Resolution) and Save:
        pygame.image.save(win,"renders/frame"+str(int(y_angle))+Save_Format)
        etm=0
        ets=cal_eta(int(y_angle) , (ms/1000))
        if ets>60:
            etm=int(ets/60)
            ets-=etm*60

            eta=str(etm)+":"+str(int(ets))
        else:
            eta=str(ets)
            
        print("fame "+str(int(y_angle))+" - eta "+str(eta)+" seconds")
    
    if FF:
        FF=False
    clock.tick(120)





pygame.quit()

if Dynamic_Resolution and (lowest[0]<1000):
    print("\n----------------------------------------------------------------")
    print("----------------------------------------------------------------")
    print("Performance Report !! \n \n")
    print('Lowest FPS : '+str(lowest[0])+' ,at '+str(int(100/int(lowest[1])))+'% Resolution')
    if lag_count==1:
        print(str(lag_count)+' lag spike')
    else:
        print(str(lag_count)+' lag spikes')
    print('\n \n')
    print('Average FPS : '+str(int(avg[0])))
    try:
        print('Average Resolution : '+str(int(100/int(avg[1])))+"%" )
    except:
        print('Average Resolution : 100%')
    print("\n \n \n----------------------------------------------------------------")
    print("----------------------------------------------------------------")
    
    
