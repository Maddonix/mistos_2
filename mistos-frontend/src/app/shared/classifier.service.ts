import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { Classifier } from "../models/classifier.model";

@Injectable({providedIn:"root"})
export class ClassifierService {
    allClassifierListChanged = new Subject<Classifier[]>();
    activeClassifier = new Subject<Classifier>();
    rfClassifierListChanged = new Subject<Classifier[]>();
    activeRfClassifier = new Subject<Classifier>();
    dfClassifierListChanged = new Subject<Classifier[]>();
    activeDfClassifier = new Subject<Classifier>();

    private allClassifierList:Classifier[] = [];
    private rfClassifierList: Classifier[] = [];
    private dfClassifierList: Classifier[] = [];

    constructor() {}
    // All

    changeActiveClassifier(classifier:Classifier) {
        this.activeClassifier.next(classifier);
    }

    getClassifierList() {
        return this.allClassifierList.slice();
    }

    getClassifier(index:number) {
        return this.allClassifierList[index];
    }

    setClassifierList(classifierList: Classifier[]){
        this.allClassifierList = classifierList;
        this.allClassifierListChanged.next(this.allClassifierList.slice());
    }

    // Random Forest Segmentation
    changeActiveRfClassifier(classifier:Classifier) {
        this.activeRfClassifier.next(classifier);
    }

    getRfClassifierList() {
        return this.rfClassifierList.slice();
    }

    getRfClassifier(index:number) {
        return this.rfClassifierList[index];
    }

    setRfClassifierList(classifierList: Classifier[]){
        this.rfClassifierList = classifierList;
        this.rfClassifierListChanged.next(this.rfClassifierList.slice());
    }

    // DeepFlash
    changeActiveDfClassifier(classifier:Classifier) {
        this.activeDfClassifier.next(classifier);
    }

    getDfClassifierList() {
        return this.dfClassifierList.slice();
    }

    setDfClassifierList(dfClassifierList:Classifier[]) {
        this.dfClassifierList = dfClassifierList;
        this.dfClassifierListChanged.next(this.dfClassifierList.slice());
    }

}
