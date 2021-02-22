import { stringify } from '@angular/compiler/src/util';
import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { MatTableFilter } from 'mat-table-filter';
import { Subscription } from 'rxjs';
import { ExperimentCreateNewDialogComponent } from 'src/app/dialogs/experiment-create-new-dialog/experiment-create-new-dialog.component';
import { Experiment } from 'src/app/models/experiment.model';
import { ComService } from 'src/app/shared/com.service';
import { ExperimentService } from 'src/app/shared/experiment.service';

@Component({
  selector: 'app-experiments-list',
  templateUrl: './experiments-list.component.html',
  styleUrls: ['./experiments-list.component.css']
})
export class ExperimentsListComponent implements AfterViewInit, OnInit {
  @ViewChild(MatSort) sort: MatSort;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  
  filterEntity: Experiment;
  filterType: MatTableFilter;
  dataSource: MatTableDataSource<Experiment>;//ImagesListDataSource;
  experimentList: Experiment[];
  subscription: Subscription;


  displayedColumns = ['uid', 'name', "tags", "actions"];

  constructor(
    private comService: ComService,
    private router: Router,
    private route: ActivatedRoute,
    public dialog: MatDialog,
  ) { }

  ngOnInit(): void {
    // // Subscribe to imagelist
    // this.subscription = this.experimentService.experimentListChanged.subscribe((experimentList:Experiment[]) => {
    //   this.experimentList = experimentList;
    // });
    // this.experimentList = this.experimentService.getExperimentList();
    this.route.data.subscribe((data:Data) => {
      this.experimentList = data["experimentList"];
    });
    // Components for filtering
    this.filterEntity = new Experiment();
    this.filterType = MatTableFilter.ANYWHERE;
    //create dataSource for table
    this.dataSource = new MatTableDataSource(this.experimentList);
  }

  onCreateNewExperiment() {
    // Define Dialog Configuration
    let dialogConfig = new MatDialogConfig();
    dialogConfig.disableClose = true; //disables closing by clicking outside of the dialog
    dialogConfig.autoFocus = true; //focus will automatically set on the first form field
    dialogConfig.hasBackdrop = true; //prevents user from clicking on the rest of the ui
    dialogConfig.closeOnNavigation = true; //closes dialog if wen navigate to another route

    const dialogRef = this.dialog.open(         //dialogRef is a observable of the dialog
      ExperimentCreateNewDialogComponent,
      dialogConfig
    );
    dialogRef.afterClosed().subscribe((newExperiment:Experiment)=> {
      if (newExperiment instanceof Experiment) {
        this.comService.createNewExperiment(newExperiment).subscribe((response) => {
          this.comService.fetchExperimentList().subscribe(experimentList => {
            this.experimentList = experimentList;
            this.onFetchData();
          });
        });
      } else {
        console.log("aborted");
      }
      
    }
  );  
  }

  onFetchData() {
    this.dataSource = new MatTableDataSource(this.experimentList);
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  ngAfterViewInit() {
    this.dataSource = new MatTableDataSource(this.experimentList);
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  onSelect(experimentId: number) {
    this.router.navigate([experimentId, "hint"], {relativeTo: this.route});
  }

  onDetail(uid) {
    this.router.navigate([uid, "detail"], {relativeTo:this.route});
  }

}
