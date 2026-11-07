import {Composition} from 'remotion';
import {YiloLineHero} from './YiloLineHero';

export const RemotionRoot = () => <><Composition id="YiloLineHero" component={YiloLineHero} width={1280} height={608} fps={24} durationInFrames={336} defaultProps={{locale:'zh-hans',artOnly:false,useH3:true}} /><Composition id="YiloPedalingAnchor" component={YiloLineHero} width={1280} height={720} fps={24} durationInFrames={336} defaultProps={{locale:'en',artOnly:true,useH3:false}} /></>;
