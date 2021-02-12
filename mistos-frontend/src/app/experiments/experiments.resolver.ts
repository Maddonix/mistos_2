import { Injectable } from "@angular/core";
import { ActivatedRouteSnapshot, Resolve, RouterStateSnapshot } from "@angular/router";
import { Observable, Subscription } from "rxjs";
import { Experiment } from "../models/experiment.model";
import { ComService } from "../shared/com.service";
import { ExperimentService } from "../shared/experiment.service";

@Injectable()
export class ExperimentListResolver implements Resolve<Experiment[]> {
    subscription:Subscription;
    experimentList:Experiment[];

    constructor(
        private comService:ComService
    ) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Experiment[]> | Promise<Experiment[]> | Experiment[] {
        return this.comService.fetchExperimentList();
        }
}

@Injectable()
export class ExperimentResolver implements Resolve<Experiment> {
    subscription:Subscription;
    experiment:Experiment;
    id: number;

    constructor(
        private comService:ComService
    ) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Experiment> | Promise<Experiment> | Experiment{
        this.id = route.params["id"];
        return this.comService.fetchExperimentById(this.id);
        }
}