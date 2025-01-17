import { Injectable } from "@angular/core";
import { ActivatedRouteSnapshot, Resolve, RouterStateSnapshot } from "@angular/router";
import { Observable, Subscription } from "rxjs";
import { Classifier } from "../models/classifier.model";
import { ClassifierService } from "../shared/classifier.service";
import { ComService } from "../shared/com.service";

@Injectable()
export class ClassifierListResolver implements Resolve<Classifier[]> {
    subscription:Subscription;
    classifierList:Classifier[];

    constructor(
        private comService:ComService
    ) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Classifier[]> | Promise<Classifier[]> | Classifier[] {
        return this.comService.fetchClassifierList();
        }
}

@Injectable()
export class ClassifierResolver implements Resolve<Classifier> {
    subscription:Subscription;
    classifier:Classifier;
    id: number;

    constructor(
        private comService:ComService
    ) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Classifier> | Promise<Classifier> | Classifier{
        this.id = route.params["id"];    
        return this.comService.fetchClassifierById(this.id);
        }
}

@Injectable()
export class RfClassifierListResolver implements Resolve<Classifier[]> {
    subscription:Subscription;
    classifierList:Classifier[];

    constructor(
        private comService:ComService
    ) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Classifier[]> | Promise<Classifier[]> | Classifier[] {
        return this.comService.fetchRfClassifierList()
        }
}

@Injectable()
export class RfClassifierResolver implements Resolve<Classifier> {
    subscription:Subscription;
    classifier:Classifier;
    id: number;

    constructor(
        private comService:ComService
    ) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Classifier> | Promise<Classifier> | Classifier{
        // this.comService.fetchExperimentList();
        this.id = route.params["id"];    
        return this.comService.fetchRfClassifierById(this.id);
        }
}

@Injectable()
export class DfClassifierListResolver implements Resolve<Classifier[]> {
    subscription:Subscription;
    classifierList:Classifier[];

    constructor(
        private comService:ComService
    ) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Classifier[]> | Promise<Classifier[]> | Classifier[] {
        return this.comService.fetchDfClassifierList()
        }
}

@Injectable()
export class DfClassifierResolver implements Resolve<Classifier> {
    subscription:Subscription;
    classifier:Classifier;
    id: number;

    constructor(
        private comService:ComService
    ) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Classifier> | Promise<Classifier> | Classifier{
        // this.comService.fetchExperimentList();
        this.id = route.params["id"];    
        return this.comService.fetchDfClassifierById(this.id);
        }
}