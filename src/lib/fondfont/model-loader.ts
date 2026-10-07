import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { fetchModelBytes } from './model-bytes.mjs';

export async function loadModel(url:string, signal?:AbortSignal) {
  const bytes = await fetchModelBytes(url, signal);
  const model = await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(bytes, url.slice(0, url.lastIndexOf('/') + 1));
  if (signal?.aborted) {
    const geometries = new Set<THREE.BufferGeometry>(), materials = new Set<THREE.Material>(), textures = new Set<THREE.Texture>();
    model.scene.traverse(object => {
      if (!(object instanceof THREE.Mesh)) return;
      geometries.add(object.geometry);
      for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
        materials.add(material);
        for (const value of Object.values(material)) if (value instanceof THREE.Texture) textures.add(value);
      }
    });
    geometries.forEach(value => value.dispose()); materials.forEach(value => value.dispose()); textures.forEach(value => value.dispose());
    signal.throwIfAborted();
  }
  return model;
}
