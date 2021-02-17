import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ClassifierDetailComponent } from './classifiers/classifier-detail/classifier-detail.component';
import { ClassifierHintComponent } from './classifiers/classifier-hint/classifier-hint.component';
import { ClassifierStartComponent } from './classifiers/classifier-start/classifier-start.component';
import { RfClassifierListResolver, RfClassifierResolver, DfClassifierListResolver, DfClassifierResolver, ClassifierListResolver, ClassifierResolver } from './classifiers/classifier.resolver';
import { ClassifiersComponent } from './classifiers/classifiers.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { DeepflashComponent } from './deepflash/deepflash.component';
import { ExperimentDetailComponent } from './experiments/experiment-detail/experiment-detail.component';
import { ExperimentHintComponent } from './experiments/experiment-hint/experiment-hint.component';
import { ExperimentStartComponent } from './experiments/experiment-start/experiment-start.component';
import { ExperimentsComponent } from './experiments/experiments.component';
import { ExperimentListResolver, ExperimentResolver } from './experiments/experiments.resolver';
import { ImageDetailComponent } from './images/image-detail/image-detail.component';
import { ImageHintComponent } from './images/image-hint/image-hint.component';
import { ImageStartComponent } from './images/image-start/image-start.component';
import { ImagesComponent } from './images/images.component';
import { ImageListResolver, ImageResolver } from './images/images.resolver';
import { ImporterComponent } from './importer/importer.component';
import { OptionsComponent } from './options/options.component';

const routes: Routes = [
  { path: "", redirectTo: "/dashboard", pathMatch: "full" },
  { path: "dashboard", component: DashboardComponent },
  { path: "images", component: ImagesComponent, resolve: {imageList: ImageListResolver}, children: [
    { path: "", component: ImageStartComponent },
    { path: ":id/hint", component: ImageHintComponent, resolve: {image:ImageResolver} }
  ] },
  { path: "images/:id/detail", component: ImageDetailComponent, resolve: {image:ImageResolver} },
  { path: "experiments", component: ExperimentsComponent, resolve: {experimentList: ExperimentListResolver}, children: [
    { path: "", component: ExperimentStartComponent },
    { path: ":id/hint", component: ExperimentHintComponent, resolve: {experiment:ExperimentResolver} }
  ]},
  { path: "experiments/:id/detail", component: ExperimentDetailComponent, resolve: {experiment:ExperimentResolver, imageList: ImageListResolver} },
  { path: "classifiers", component: ClassifiersComponent, resolve: {classifierList: ClassifierListResolver }, children: [
    { path: "", component: ClassifierStartComponent },
    { path: ":id/hint", component: ClassifierHintComponent, resolve: {classifier:ClassifierResolver} }
  ] },
  { path: "deepflash", component: DeepflashComponent, resolve: {imageList: ImageListResolver, dfClassifierList: DfClassifierListResolver} },
  { path: "classifiers/:id/detail", component: ClassifierDetailComponent, resolve: { classifier: ClassifierResolver } },
  { path: "import", component: ImporterComponent },
  { path: "options", component: OptionsComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
