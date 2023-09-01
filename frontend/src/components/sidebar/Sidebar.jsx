import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router';

import * as S from './style';
import { GetProjectList } from 'apis/ProjectAPIs';
import { GetContainerList } from 'apis/ContainerAPIs';

export default function Sidebar() {
    const [projectState, setProjectState] = useState({});
    const location = useLocation();

    // 프로젝트 리스트
    useEffect(() => {
        const getProjectList = async () => {
            const result = await GetProjectList();
            const state = {};

            result.forEach((res) => {
                state[res.name] = {
                    "open": false,
                    "list": [],
                };
            });

            setProjectState(state);
        }

        getProjectList();
    }, []);

    const onClickProject = async (project) => {
        const update = { ...projectState };

        if (update[project].open) {
            update[project].list = [];
        } else {
            const getContainerList = async (projectName) => {
                const result = await GetContainerList(projectName);

                update[project].list = result;
            }

            await getContainerList(project);
        }

        update[project].open = !update[project].open;

        setProjectState(update);
    }

    const onClickConatiner = (container) => {
        window.location.pathname = window.location.pathname.replace(location.pathname, "") + "ide/" + container + "/";
    }

    return (
        <S.Section>
            <S.Header>
                <h2>projects</h2>
            </S.Header>
            <S.List>
                {
                    Object.keys(projectState).map(project => {
                        return (
                            <li key={project}>
                                <S.ListButton onClick={() => onClickProject(project)}>
                                    {
                                        projectState[project].open ? <i className="fas fa-chevron-down"></i> : <i className="fas fa-chevron-right"></i>
                                    }
                                    <i className="far fa-folder"></i>
                                    <span>{project}</span>
                                </S.ListButton>
                                <S.ContainerList>
                                    {
                                        projectState[project].open ?
                                            projectState[project].list.map(container => {
                                                return (
                                                    <li key={container.name}>
                                                        <S.ContainerButton onClick={() => onClickConatiner(container.name)}>
                                                            {/* <i className="far fa-file"></i> */}
                                                            <i className="fab fa-docker"></i>
                                                            <span>{container.name}</span>
                                                        </S.ContainerButton>
                                                    </li>
                                                )
                                            })
                                            : <></>
                                    }
                                </S.ContainerList>
                            </li>
                        )
                    })
                }
            </S.List>
        </S.Section>
    )
}
