import { stringify } from '@angular/compiler/src/util';
import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource } from '@angular/material/table';
import { ActivatedRoute, Data, Router } from '@angular/router';
import { MatTableFilter } from 'mat-table-filter';
import { Subscription } from 'rxjs';
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
    private experimentService: ExperimentService,
    private router: Router,
    private route: ActivatedRoute
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
