import { HttpClient, HttpEvent, HttpEventType, HttpRequest } from "@angular/common/http";
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

    fetchImageThumbnailPath(imageId) {
        let url = this.serverURL.concat("images/fetch_thumbnail_path/");
        url = url.concat(imageId.toString());
        return this.httpClient.get(
            url
            ).pipe(
                map(
                    (data: string) => {
                        return data
                    },
                    (error) => {
                        return error
                    }
                )
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

    uploadImages(file:File, uploadMode:string) {
        const formData: FormData = new FormData();
        formData.append('file', file);

        if (uploadMode === "image") {
            return this.httpClient.post(`${this.serverURL}images/upload`, formData, {
                reportProgress: true,
                observe: 'events'
                }).pipe(
                    map((event)=>{
                        switch(event.type) {
                            case HttpEventType.UploadProgress:
                                const progress = Math.round(100 * event.loaded / event.total);
                                return {status: "progress", message: progress};
                                
                            case HttpEventType.Response:
                                return event.body;
                            
                            default:
                                return "Unhandled event: ${event.type}";
                        }
                    })
                );
        } else {
            return this.httpClient.post(`${this.serverURL}images/upload_max_z_projection`, formData, {
                reportProgress: true,
                observe: 'events'
                }).pipe(
                    map((event)=>{
                        switch(event.type) {
                            case HttpEventType.UploadProgress:
                                const progress = Math.round(100 * event.loaded / event.total);
                                return {status: "progress", message: progress};
                                
                            case HttpEventType.Response:
                                return event.body;
                            
                            default:
                                return "Unhandled event: ${event.type}";
                        }
                    })
            );
        }
    }

    uploadImagesToGroup(file:File, groupId:string) {
        const formData: FormData = new FormData();
        // formData.append('group_id', groupId.toString());
        formData.append('file', file);

        return this.httpClient.post(`${this.serverURL}images/upload_to_group_${groupId}`, formData, {
            reportProgress: true,
            observe: 'events'
            }).pipe(
                map((event)=>{
                    switch(event.type) {
                        case HttpEventType.UploadProgress:
                            const progress = Math.round(100 * event.loaded / event.total);
                            return {status: "progress", message: progress};
                            
                        case HttpEventType.Response:
                            return event.body;
                        
                        default:
                            return "Unhandled event: ${event.type}";
                    }
            })
        );
        
    }

    uploadImageFromFilepath(path:string, uploadMode:string) {
        let payload = {path: path};
        if (uploadMode === "image") {
            return this.httpClient.post(`${this.serverURL}images/read_from_path`, payload);
        } else {
            return this.httpClient.post(`${this.serverURL}images/read_from_path_max_z_projection`, payload)
        }
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

    exportMistosImage(imageId:number) {
        let url = this.serverURL.concat("images/export_mistos_image/");
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
                )
            )
    }

    importMistosImage(path) {
        let payload = {path: path};
        return this.httpClient.post(`${this.serverURL}images/import_mistos_image`, payload);
    }

    // Classifier + Deepflash
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

    fetchClassifierById(classifierId:number){
        let url = this.serverURL.concat("classifier/fetch_rf_by_id/");
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

    fetchRfClassifierList() {
        return this.httpClient.get(this.serverURL.concat("classifier/fetch_all_rf"))
        .pipe(
            map((data:Classifier[])=>{
                return data
            },
            (error)=>{
                return error
            }
            ),
            tap((data:Classifier[])=>{
                this.classifierService.setRfClassifierList(data);
            })
        )
    }

    fetchRfClassifierById(classifierId:number){
        let url = this.serverURL.concat("classifier/fetch_rf_by_id/");
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
                    this.classifierService.changeActiveRfClassifier(data);
                })
            )
    }

    uploadDeepflashModels(file:File) {
    const formData: FormData = new FormData();
    formData.append('file', file);

    return this.httpClient.post(`${this.serverURL}deepflash/upload_model`, formData, {
        reportProgress: true,
        observe: 'events'
        }).pipe(
            map((event)=>{
                switch(event.type) {
                    case HttpEventType.UploadProgress:
                        const progress = Math.round(100 * event.loaded / event.total);
                        return {status: "progress", message: progress};
                        
                    case HttpEventType.Response:
                        return event.body;
                    
                    default:
                        return "Unhandled event: ${event.type}";
                }
            })
        );
    } 

    uploadDfModelFromFilepath(path:string) {
        let payload = {path: path}; 
            return this.httpClient.post(`${this.serverURL}deepflash/read_from_path`, payload);
    } 

    estimateGroundTruth(imagesLabelsDict) {
        return this.httpClient.post(
            this.serverURL.concat("deepflash/estimate_ground_truth"), // URL
            {"images_label_dict": imagesLabelsDict}
        )
    }

    fetchDfClassifierList(){
        return this.httpClient.get(this.serverURL.concat("classifier/fetch_all_df"))
        .pipe(
            map((data:Classifier[])=>{
                return data
            },
            (error)=>{
                return error
            }
            ),
            tap((data:Classifier[])=>{
                this.classifierService.setDfClassifierList(data);
            })
        )
    }

    fetchDfClassifierById(classifierId:number){
        let url = this.serverURL.concat("classifier/fetch_df_by_id/");
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
                    this.classifierService.changeActiveDfClassifier(data);
                })
            )
    }

    deleteClassifierById(classifierId:number) {
        return this.httpClient.post(
            this.serverURL.concat("classifier/delete_by_id"), // URL
            {
                "id": classifierId
            }
        )
    }

    updateClassifierName(classifierId:number, newName: string) {
        return this.httpClient.post(
            this.serverURL.concat("classifier/update_name"), // URL
            {
                "id": classifierId,
                "new_name": newName
            }
        ) 
    }

    deepflashPredictImages(classifierId:number, imageIds:number[]) {
        return this.httpClient.post(
            this.serverURL.concat("deepflash/predict_images"),
            {
                "classifier_id": classifierId,
                "channel": 0,
                "image_ids": imageIds,
                "use_tta": false
            }
        )
    }

    deepflashPredictImages3D(classifierId:number, channel:number, imageIds:number[]) {
        return this.httpClient.post(
            this.serverURL.concat("deepflash/predict_images_3d"),
            {
                "classifier_id": classifierId,
                "channel": channel,
                "image_ids": imageIds,
                "use_tta": false
            }
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

    exportMistosExperiment(experimentId:number) {
        let url = this.serverURL.concat("experiments/export_mistos_experiment/");
        url = url.concat(experimentId.toString());
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
                )
            )
    }

    importMistosExperiment(path) {
        let payload = {path: path};
        return this.httpClient.post(`${this.serverURL}experiments/import_mistos_experiment`, payload);
    }

}