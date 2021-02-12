import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { Classifier } from "../models/classifier.model";

@Injectable({providedIn:"root"})
export class ClassifierService {
    classifierListChanged = new Subject<Classifier[]>();
    activeClassifier = new Subject<Classifier>();

    private classifierList: Classifier[] = [];

    constructor() {}

    changeActiveClassifier(classifier:Classifier) {
        this.activeClassifier.next(classifier);
    }

    getClassifierList() {
        return this.classifierList.slice();
    }

    getClassifier(index:number) {
        return this.classifierList[index];
    }

    setClassifierList(classifierList: Classifier[]){
        this.classifierList = classifierList;
        this.classifierListChanged.next(this.classifierList.slice());
    }

}
