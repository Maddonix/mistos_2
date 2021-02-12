import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { Experiment } from "../models/experiment.model";

@Injectable({providedIn:"root"})
export class ExperimentService {
    experimentListChanged = new Subject<Experiment[]>();
    activeExperiment = new Subject<Experiment>();

    private experimentList: Experiment[] = [];

    constructor() {}

    changeActiveExperiment(experiment:Experiment) {
        this.activeExperiment.next(experiment);
    }

    getExperimentList() {
        return this.experimentList.slice();
    }

    getExperiment(index:number) {
        return this.experimentList[index];
    }

    setExperimentList(experimentList: Experiment[]){
        this.experimentList = experimentList;
        this.experimentListChanged.next(this.experimentList.slice());
    }
}