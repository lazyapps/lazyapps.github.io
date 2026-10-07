// Registered ground-plane axes of the imagegen oval-road plate.
export const WIDTH=1672;
export const HEIGHT=941;
export const AX=560/10.8, AZ=-90/5.2, BX=74/10.8, BZ=111/5.2;
export const OX=480-AX*(-5.6)-AZ*4.3;
export const OY=489-BX*(-5.6)-BZ*4.3;
export const VERTICAL=45;
export function projectWorld(x,y,z){return{x:OX+AX*x+AZ*z,y:OY+BX*x+BZ*z-VERTICAL*y,depth:.3*x+.9*z+.15*y};}
export function unprojectGround(u,v){const dx=u-OX,dy=v-OY,det=AX*BZ-AZ*BX;return{x:(dx*BZ-AZ*dy)/det,z:(AX*dy-dx*BX)/det};}
