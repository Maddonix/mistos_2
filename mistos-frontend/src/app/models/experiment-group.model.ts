import { Image } from "./image.model"

export class ExperimentGroup {
    uid: number;
    experimentId: number;
    name: string;
    hint: string;
    description: string;
    images: Image[];
    resultLayerIds: number[];
}