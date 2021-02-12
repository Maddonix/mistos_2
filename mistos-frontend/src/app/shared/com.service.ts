import { HttpClient, HttpEvent, HttpRequest } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Router } from "@angular/router";
import { Observable } from "rxjs";
import { map, tap } from "rxjs/operators";
import { Classifier } from "../models/classifier.model";
import { Image } from "../models/image.model";
import { ExperimentService } from "./experiment.service";
import { ImageService } from "./image.service";
import { ClassifierService } from "./classifier.service";
import { Experiment } from "../models/experiment.model";

@Injectable({providedIn:"root"})
export class ComService {
    // /**
    //  * Constructor
    //  * @param httpClient Inject the http client
    //  * @param router Inject the router
    //  */
    constructor(
        private httpClient: HttpClient, 
        private router: Router,
        private imageService: ImageService,
        private experimentService: ExperimentService,
        private classifierService: ClassifierService
    ){​​​​ }​​​​

    serverURL = "http://localhost:7777/api/"

    // Images
    fetchImageList() {
        return this.httpClient.get(this.serverURL.concat("images/fetch_all"))
        .pipe(
            map(
                (data: Image[]) => {
                    return data
                },
                (error) => {
                    return error
                }
            ),
            tap((data:Image[]) => {
                this.imageService.setImageList(data);
                }
            )
        )
    }

    fetchImageById(imageId) {
        let url = this.serverURL.concat("images/fetch_by_id/");
        url = url.concat(imageId.toString());
        return this.httpClient.get(
            url
            ).pipe(
                map(
                    (data: Image) => {
                        return data
                    },
                    (error) => {
                        return error
                    }
                ),
                tap((data:Image) => {
                    this.imageService.changeActiveImage(data);
                })
            )
    }

    viewImage(imageId:number, displayResultLayers:boolean = false, displayBackgroundLayer: boolean = false) {
        this.httpClient.post(
                this.serverURL.concat("images/view_by_id"), // URL
                {"image_id": imageId, "display_result_layers": displayResultLayers, "display_background_layers":displayBackgroundLayer}
                // body, as third argument we could add options. This is not required here.
            ).subscribe((response) => {
            console.log("View Image Request:");
            console.log(response);
        });
    }

    uploadImage(file:File):Observable<HttpEvent<any>> {
        const formData: FormData = new FormData();
    
        formData.append('file', file);
    
        const req = new HttpRequest('POST', `${this.serverURL}images/upload`, formData//, {
        //   reportProgress: true,
        //   responseType: 'json'
        // }
        );
    
        return this.httpClient.request(req);
      }

    deleteImageById(imageId:number) {
        return this.httpClient.post(
            this.serverURL.concat("images/delete_by_id"), // URL
            {"id": imageId}
            // body, as third argument we could add options. This is not required here.
        )
    }

    updateImageHint(imageId: number, newHint:string) {
        return this.httpClient.post(
            this.serverURL.concat("images/update_image_hint"), // URL
            {
                "id": imageId,
                "new_hint": newHint
            }
        )
    }

    updateImageChannelNames(imageId:number, channelNames:string[]) {
        console.log("IMAGE ID");
        console.log(imageId)
        return this.httpClient.post(
            this.serverURL.concat("images/update_image_channel_names"), // URL
            {
                "image_id": imageId,
                "channel_names": channelNames
            }
        )
    }

    updateLayerHint(layerId:number, newHint:string) {
        return this.httpClient.post(
            this.serverURL.concat("images/update_layer_hint"), // URL
            {
                "id": layerId,
                "new_hint": newHint
            }
        )
    }

    updateLayerName(layerId:number, newName:string) {
        return this.httpClient.post(
            this.serverURL.concat("images/update_layer_name"), // URL
            {
                "id": layerId,
                "new_name": newName
            }
        ) 
    }

    deleteResultLayer(layerId:number) {
        return this.httpClient.post(
            this.serverURL.concat("images/delete_layer"), // URL
            {
                "id": layerId
            }
        ) 
    }

    // Classifier
    fetchClassifierList() {
        return this.httpClient.get(this.serverURL.concat("classifier/fetch_all"))
        .pipe(
            map((data:Classifier[])=>{
                return data
            },
            (error)=>{
                return error
            }
            ),
            tap((data:Classifier[])=>{
                this.classifierService.setClassifierList(data);
            })
        )
    }

    fetchClassifierById(classifierId){
        let url = this.serverURL.concat("classifier/fetch_by_id/");
        url = url.concat(classifierId.toString());

        return this.httpClient.get(
            url
            ).pipe(
                map(
                    (data: Classifier) => {
                        return data
                    },
                    (error) => {
                        return error
                    }
                ),
                tap((data:Classifier) => {
                    this.classifierService.changeActiveClassifier(data);
                })
            )
    }

    // Experiments
    fetchExperimentList() {
        return this.httpClient.get(this.serverURL.concat("experiments/fetch_all"))
        .pipe(
            map((data:Experiment[])=>{
                return data
            },
            (error)=>{
                return error
            }
            ),
            tap((data:Experiment[])=>{
                this.experimentService.setExperimentList(data);
            })
        );
    }

    fetchExperimentById(experimentId) {
        let url = this.serverURL.concat("experiments/fetch_by_id/");
        url = url.concat(experimentId.toString());
        return this.httpClient.get(
            url
            ).pipe(
                map(
                    (data: Experiment) => {
                        return data
                    },
                    (error) => {
                        return error
                    }
                ),
                tap((data:Experiment) => {
                    this.experimentService.changeActiveExperiment(data);
                })
            )
    }

    createNewExperiment(experiment:Experiment) {
        return this.httpClient.post(
            this.serverURL.concat(
                "experiments/create_new_experiment"), // URL
                {"experiment": experiment}
        )
    }

    newExperimentGroup(experimentId:number) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/new_group_by_id"), // URL
            {"experiment_id": experimentId}
        )
    }

    addResultLayertoGroup(groupId:number, layerId:number) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/add_result_layer_to_group"), // URL
            {
                "group_id": groupId,
                "layer_id": layerId
            }
        ) 
    }

    calculateExperimentResults(experimentId:number) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/calculate_results"), // URL
            {"experiment_id": experimentId}
        )
    }

    updateExperimentName(experimentId:number, newName:string) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/update_experiment_name"), // URL
            {
                "id": experimentId,
                "new_name": newName
            }
        ) 
    }

    updateExperimentHint(experimentId:number, newHint:string) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/update_experiment_hint"), // URL
            {
                "id": experimentId,
                "new_hint": newHint
            }
        )
    }

    updateExperimentDescription(experimentId:number, newDescription:string) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/update_experiment_description"), // URL
            {
                "id": experimentId,
                "new_description": newDescription
            }
        )
    }

    updateExperimentGroupImages(groupId:number, imageIdList:number[]) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/update_experiment_group_images"), // URL
            {
                "group_id": groupId,
                "image_id_list": imageIdList
            }
        )
    }

    updateExperimentGroupName(experimentGroupId:number, newName:string) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/update_experiment_group_name"), // URL
            {
                "id": experimentGroupId,
                "new_name": newName
            }
        ) 
    }

    updateExperimentGroupHint(groupId:number, newHint:string) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/update_experiment_group_hint"), // URL
            {
                "id": groupId,
                "new_hint": newHint
            }
        )
    }

    updateExperimentGroupDescription(groupId:number, newDescription:string) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/update_experiment_group_description"), // URL
            {
                "id": groupId,
                "new_description": newDescription
            }
        )
    }

    deleteExperimentGroup(experimentId:number, groupId:number) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/delete_group_by_id"), // URL
            {
                "experiment_id": experimentId, 
                "group_id":groupId
            }
        )
    }

    deleteExperiment(experimentId:number) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/delete_by_id"), 
            {
                "experiment_id": experimentId
            }
        )
    }
    
    deleteImageFromExperimentGroup(groupId:number, imageId:number) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/delete_image_from_experiment_group"), 
            {
                "group_id": groupId,
                "image_id": imageId
            }
        )
    }

    exportExperiment(experimentId:number, exportRequest) {
        return this.httpClient.post(
            this.serverURL.concat("experiments/export_experiment"), 
            {
                "experiment_id": experimentId,
                "export_request": exportRequest
            }
        )
    }

}