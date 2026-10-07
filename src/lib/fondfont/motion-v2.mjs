// Coordinates are registered to the imagegen master plate, with y down.
export const DURATION = 22;
export const SOURCE = 704;
export const DESTINATION = 1130;
export const DECK = 610;
export const DOCK = 618;
export const ROAD_SLOPE = 44 / (DESTINATION - SOURCE);
export const WHEEL_RADIUS = 33;
export const RIG_HEIGHT = 177.5;
export const smooth = (a, b, t) => {
  const p = Math.max(0, Math.min(1, (t - a) / (b - a)));
  return p * p * (3 - 2 * p);
};
const mix = (a,b,t) => a+(b-a)*t;

export function sampleMotion(seconds) {
  const t = Math.max(0, Math.min(DURATION,seconds));
  const drive = smooth(4.8,8.8,t);
  const back = smooth(17.8,21.8,t);
  const distance = (DESTINATION-SOURCE)*(drive-back);
  const truck = {x:SOURCE+distance,y:DECK+distance*ROAD_SLOPE,distance};
  const destinationDeck = DECK+(DESTINATION-SOURCE)*ROAD_SLOPE;
  let cargo = {x:SOURCE,y:mix(515,DECK,smooth(1.2,3.2,t))};
  let source = {x:SOURCE,y:cargo.y-RIG_HEIGHT};
  let receiver = {x:DESTINATION,y:347};
  let phase = 0;
  if(t>=3.2)source.y=mix(DECK-RIG_HEIGHT,347,smooth(3.7,4.6,t));
  if(t>=4.8){cargo={x:truck.x,y:truck.y};phase=2;}
  else if(t>=1.2)phase=1;
  if(t>=8.8){
    phase=3;
    receiver.y=mix(347,destinationDeck-RIG_HEIGHT,smooth(9,10,t));
  }
  if(t>=10.5){
    const shift = smooth(12.6,13.6,t);
    cargo={x:DESTINATION+64*shift,y:destinationDeck-141*smooth(10.5,12.2,t)-34*shift+139*smooth(13.8,15.5,t)};
    receiver={x:cargo.x,y:cargo.y-RIG_HEIGHT};
  }
  if(t>=15.5){
    cargo={x:DESTINATION+64,y:DOCK};
    receiver={x:cargo.x,y:mix(DOCK-RIG_HEIGHT,347,smooth(16.1,17.2,t))};
  }
  if(t>=16.1)phase=4;
  return {t,truck,cargo,source,receiver,phase,finish:smooth(16.1,17.1,t),complete:t===DURATION};
}

export const wheelTravel = seconds => sampleMotion(seconds).truck.distance;
