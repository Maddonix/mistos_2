import { ImageResultLayer } from "./image-result-layer.model";
import { Measurement } from "./measurement.model";

export class Image{
    uid: number;
    seriesIndex: number;
    name: string = "";
    hasBgLayer: boolean;
    bgLayerId: number; // might be null when image without bg layer is passed
    metadata: {};
    hint: string = "";
    imageResultLayers: ImageResultLayer[] = [];
    measurements: Measurement[] = [];
    tags: string[] = [];
}