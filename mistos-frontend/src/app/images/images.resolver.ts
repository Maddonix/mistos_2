import { CdkNoDataRow } from "@angular/cdk/table";
import { Injectable } from "@angular/core";
import { ActivatedRouteSnapshot, Params, Resolve, RouterStateSnapshot } from "@angular/router";
import { Observable, Subscription } from "rxjs";

import { Image } from "../models/image.model";
import { ComService } from "../shared/com.service";
import { ImageService } from "../shared/image.service";

@Injectable()
export class ImageListResolver implements Resolve<Image[]> {
    subscription:Subscription;
    imageList:Image[];

    constructor(
        private imageService:ImageService,
        private comService:ComService
    ) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Image[]> | Promise<Image[]> | Image[] {
        return this.comService.fetchImageList()
        }
}

@Injectable()
export class ImageResolver implements Resolve<Image> {
    subscription:Subscription;
    image:Image;
    id:number;

    constructor(
        private imageService:ImageService,
        private comService:ComService
    ) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Image> | Promise<Image> | Image{
        this.id = +route.params["id"];
        return this.comService.fetchImageById(this.id)
        }
}