import * as THREE from 'three';
import { ROAD, TURN_RADIUS, TURN_X } from './motion.mjs';

/**
 * Physical perspective lens for the campus hero.
 *
 * The earlier orthographic view kept far edges as long as near edges, which reads as
 * reverse perspective on roofs and the road. A long lens on the same 33° view axis
 * restores natural foreshortening (near larger, far smaller) without fisheye distortion.
 */
export const VIEW_AXIS = new THREE.Vector3(0, 19, 29.5).normalize();
/** Distance from the framing target to the lens, in metres. The field of view is solved per viewport (fitLens). */
export const CAMERA_DISTANCE = 52;
/** Outer edge of the curb around the stadium road. */
export const CURB_RADIUS = TURN_RADIUS + 2.06;

export function createCampusCamera() {
  return new THREE.PerspectiveCamera(20, 3, 1, 260);
}

/** Outer curb outline of the stadium road on the ground plane. */
export function roadOutline(samples = 24) {
  const points: THREE.Vector3[] = [], cz = ROAD - TURN_RADIUS;
  for (const side of [1, -1]) for (let i = 0; i <= samples; i++) {
    const a = -Math.PI / 2 + Math.PI * i / samples;
    points.push(new THREE.Vector3(side * (TURN_X + CURB_RADIUS * Math.cos(a)), 0, cz + side * CURB_RADIUS * Math.sin(a)));
  }
  return points;
}

/** Bounds of points in lens tangent space (x/depth, y/depth), independent of the field of view. */
export function tangentBounds(camera: THREE.Camera, points: Iterable<THREE.Vector3>, bounds = new THREE.Box2()) {
  camera.updateMatrixWorld(true);
  const p = new THREE.Vector3(), t = new THREE.Vector2();
  for (const point of points) {
    p.copy(point).applyMatrix4(camera.matrixWorldInverse);
    bounds.expandByPoint(t.set(p.x / -p.z, p.y / -p.z));
  }
  return bounds;
}

/** Place the lens on the view axis so the given tangent-space centre falls on the optical axis. */
export function aimCamera(camera: THREE.PerspectiveCamera, target: THREE.Vector3, points: () => Iterable<THREE.Vector3>) {
  for (let pass = 0; pass < 4; pass++) {
    camera.position.copy(target).addScaledVector(VIEW_AXIS, CAMERA_DISTANCE);
    camera.lookAt(target);camera.updateMatrixWorld(true);
    const centre = tangentBounds(camera, points()).getCenter(new THREE.Vector2());
    const right = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0);
    const up = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
    target.addScaledVector(right, centre.x * CAMERA_DISTANCE).addScaledVector(up, centre.y * CAMERA_DISTANCE);
  }
  camera.position.copy(target).addScaledVector(VIEW_AXIS, CAMERA_DISTANCE);
  camera.lookAt(target);camera.updateMatrixWorld(true);
}

/**
 * Choose the field of view so the projected curb spans `roadPixels` of a `width`-pixel stage,
 * then extend the frustum upwards by `sky` pixels without moving the lens (a vertical lens shift).
 */
export function fitLens(camera: THREE.PerspectiveCamera, roadPixels: number, width: number, height: number, sky: number) {
  const span = tangentBounds(camera, roadOutline()), tanX = (span.max.x - span.min.x) * width / (2 * Math.max(roadPixels, 1));
  camera.aspect = width / height;
  camera.fov = THREE.MathUtils.radToDeg(2 * Math.atan(tanX / camera.aspect));
  camera.setViewOffset(width, height, 0, -sky, width, height + sky);
  camera.updateProjectionMatrix();
}

/** World point where the ray through a normalised device coordinate meets a plane. */
export function rayToPlane(camera: THREE.Camera, ndcX: number, ndcY: number, plane: THREE.Plane) {
  const near = new THREE.Vector3(ndcX, ndcY, -1).unproject(camera), far = new THREE.Vector3(ndcX, ndcY, 1).unproject(camera);
  return plane.intersectLine(new THREE.Line3(near, far), new THREE.Vector3()) ?? far;
}

/** Visible world width per canvas pixel at a point, for screen-space effects. */
export function metresPerPixel(camera: THREE.PerspectiveCamera, point: THREE.Vector3, canvasHeight: number) {
  const depth = point.clone().applyMatrix4(camera.matrixWorldInverse).z;
  const fullHeight = 2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * -depth;
  return fullHeight * (camera.view ? camera.view.height / camera.view.fullHeight : 1) / canvasHeight;
}
