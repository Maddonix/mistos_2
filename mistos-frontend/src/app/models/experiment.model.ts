import { ExperimentGroup } from "./experiment-group.model"

export class Experiment {
    uid: number;
    name: string;
    hint: string;
    description: string;
    tags: [];
    experimentGroups: ExperimentGroup[];
}