import { BrowserModule } from '@angular/platform-browser';
import { CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ImagesComponent } from './images/images.component';
import { ImagesListComponent } from './images/images-list/images-list.component';
import { ImageHintComponent } from './images/image-hint/image-hint.component';
import { ImageDetailComponent } from './images/image-detail/image-detail.component';
import { ExperimentsComponent } from './experiments/experiments.component';
import { ExperimentsListComponent } from './experiments/experiments-list/experiments-list.component';
import { ExperimentHintComponent } from './experiments/experiment-hint/experiment-hint.component';
import { ExperimentDetailComponent } from './experiments/experiment-detail/experiment-detail.component';
import { ImporterComponent } from './importer/importer.component';
import { ClassifiersComponent } from './classifiers/classifiers.component';
import { ClassifiersListComponent } from './classifiers/classifiers-list/classifiers-list.component';
import { ClassifierHintComponent } from './classifiers/classifier-hint/classifier-hint.component';
import { ClassifierDetailComponent } from './classifiers/classifier-detail/classifier-detail.component';
import { OptionsComponent } from './options/options.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from "@angular/common/http"

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule} from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { MatDialogModule } from "@angular/material/dialog";
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { LayoutModule } from '@angular/cdk/layout';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { AppNavbarComponent } from './app-navbar/app-navbar.component';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { FlexLayoutModule } from '@angular/flex-layout';
import { MatTableFilterModule } from 'mat-table-filter';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFileUploadModule } from 'mat-file-upload';
import { ExperimentStartComponent } from './experiments/experiment-start/experiment-start.component';
import { ImageStartComponent } from './images/image-start/image-start.component';
import { ClassifierStartComponent } from './classifiers/classifier-start/classifier-start.component';
import { ExperimentListResolver, ExperimentResolver } from './experiments/experiments.resolver';
import { RfClassifierListResolver, DfClassifierListResolver, RfClassifierResolver, DfClassifierResolver, ClassifierListResolver, ClassifierResolver } from './classifiers/classifier.resolver';
import { ImageListResolver, ImageResolver } from './images/images.resolver';
import { ExperimentCreateNewDialogComponent } from './dialogs/experiment-create-new-dialog/experiment-create-new-dialog.component';
import { MatFormFieldModule } from '@angular/material/form-field';
import { EditHintComponent } from './dialogs/edit-hint/edit-hint.component';
import { EditChannelsComponent } from './dialogs/edit-channels/edit-channels.component';
import { NgxDropzoneModule } from 'ngx-dropzone';
import { EditDescriptionComponent } from './dialogs/edit-description/edit-description.component';
import { EditNameComponent } from './dialogs/edit-name/edit-name.component';
import { AddImageToGroupComponent } from './dialogs/add-image-to-group/add-image-to-group.component';
import { ExportExperimentComponent } from './dialogs/export-experiment/export-experiment.component';
import { DeepflashComponent } from './deepflash/deepflash.component';
import { GroundTruthEstimatorComponent } from './deepflash/ground-truth-estimator/ground-truth-estimator.component';
import { PredictComponent } from './deepflash/predict/predict.component';
import { MatTabsModule } from '@angular/material/tabs';
import { WarningDeleteComponent } from './dialogs/warning-delete/warning-delete.component';
import { MistosFormatsComponent } from './importer/mistos-formats/mistos-formats.component';
import { DeepflashModelsComponent } from './importer/deepflash-models/deepflash-models.component';
import { ImagesUploadComponent } from './importer/images-upload/images-upload.component';
import { UploadImageToGroupComponent } from './dialogs/upload-image-to-group/upload-image-to-group.component';


@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    DashboardComponent,
    ImagesComponent,
    ImagesListComponent,
    ImageHintComponent,
    ImageDetailComponent,
    ExperimentsComponent,
    ExperimentsListComponent,
    ExperimentHintComponent,
    ExperimentDetailComponent,
    ImporterComponent,
    ClassifiersComponent,
    ClassifiersListComponent,
    ClassifierHintComponent,
    ClassifierDetailComponent,
    OptionsComponent,
    AppNavbarComponent,
    ExperimentStartComponent,
    ImageStartComponent,
    ClassifierStartComponent,
    ExperimentCreateNewDialogComponent,
    EditHintComponent,
    EditChannelsComponent,
    EditDescriptionComponent,
    EditNameComponent,
    AddImageToGroupComponent,
    ExportExperimentComponent,
    DeepflashComponent,
    GroundTruthEstimatorComponent,
    PredictComponent,
    WarningDeleteComponent,
    MistosFormatsComponent,
    DeepflashModelsComponent,
    ImagesUploadComponent,
    UploadImageToGroupComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MatButtonModule,
    MatMenuModule,
    MatToolbarModule,
    MatIconModule,
    MatCardModule,
    MatInputModule,
    MatSelectModule,
    MatRadioModule,
    MatDialogModule,
    FormsModule,
    MatFormFieldModule,
    ReactiveFormsModule,
    FlexLayoutModule,
    LayoutModule,
    MatSidenavModule,
    MatListModule,
    MatGridListModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatTableFilterModule,
    MatCheckboxModule,
    MatFileUploadModule,
    NgxDropzoneModule,
    MatTabsModule
  ],
  exports: [
  ],
  providers: [
    ExperimentListResolver, ExperimentResolver,
    ClassifierListResolver, ClassifierResolver,
    RfClassifierListResolver, RfClassifierResolver,
    DfClassifierListResolver, DfClassifierResolver,
    ImageListResolver, ImageResolver
  ],
  schemas: [
    CUSTOM_ELEMENTS_SCHEMA
  ],
  bootstrap: [AppComponent],
  entryComponents: [
    AddImageToGroupComponent,
    ExperimentCreateNewDialogComponent, 
    EditChannelsComponent, 
    EditHintComponent, 
    EditDescriptionComponent,
    EditNameComponent,
    ExportExperimentComponent,
    WarningDeleteComponent
  ]
})
export class AppModule { }
