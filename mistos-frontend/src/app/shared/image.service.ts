import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { Image } from "../models/image.model";

@Injectable({providedIn:"root"})
export class ImageService {
    imageListChanged = new Subject<Image[]>();
    activeImage = new Subject<Image>();

    private imageList: Image[] = [];

    constructor() {}

    changeActiveImage(image:Image) {
        this.activeImage.next(image);
    }

    getImageList() {
        return this.imageList.slice();
    }

    getImage(index:number) {
        return this.imageList[index];
    }

    setImageList(imageList: Image[]){
        this.imageList = imageList;
        this.imageListChanged.next(this.imageList.slice());
    }
}
